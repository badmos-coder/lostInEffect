#!/usr/bin/env python3
"""
Integrated Fingerprint Template and Video Recorder
Captures fingerprint templates from Arduino and records video from ESP32-CAM
with synchronized naming and session management.
Version 1.1
"""

import serial
import serial.tools.list_ports
import time
import os
import requests
import cv2
import numpy as np
from datetime import datetime
import sys
import binascii
import json
import threading
import uuid

class IntegratedCaptureSystem:
    def __init__(self, baudrate=115200, output_dir="capture_sessions", esp32_ip="192.168.4.1"):
        self.baudrate = baudrate
        self.output_dir = output_dir
        self.esp32_ip = esp32_ip
        self.esp32_url = f"http://{self.esp32_ip}"
        self.serial_port = None
        self.running = False
        self.current_session = None
        self.esp32_connected = False

        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}")

    def generate_session_id(self):
        """Generate a unique session ID for the fingerprint-video pair."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"SESSION_{timestamp}_{unique_id}"

    def find_arduino_port(self):
        """Automatically detect the Arduino/serial port."""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Look for common keywords in port descriptions
            if any(keyword in port.description.lower() for keyword in ['arduino', 'ch340', 'usb serial', 'cp210x']):
                print(f"Found potential Arduino port: {port.device}")
                return port.device
        return None

    def connect_arduino(self):
        """Establish a connection with the Arduino."""
        port = self.find_arduino_port()
        if not port:
            print("Could not find Arduino port automatically. Please select one.")
            ports = serial.tools.list_ports.comports()
            if not ports:
                print("No serial ports found!")
                return False
            for i, p in enumerate(ports):
                print(f"  {i+1}: {p.device} - {p.description}")
            try:
                choice = int(input("Enter port number: ")) - 1
                if 0 <= choice < len(ports):
                    port = ports[choice].device
                else:
                    print("Invalid selection.")
                    return False
            except (ValueError, IndexError):
                print("Invalid input.")
                return False
        
        try:
            self.serial_port = serial.Serial(port, self.baudrate, timeout=1)
            time.sleep(2) # Wait for the serial port to initialize
            self.serial_port.flushInput()
            print(f"Successfully connected to Arduino on {port}")
            return True
        except serial.SerialException as e:
            print(f"Error connecting to {port}: {e}")
            return False

    def test_esp32_connection(self):
        """Check if the ESP32-CAM is reachable."""
        print(f"Testing connection to ESP32-CAM at {self.esp32_url}...")
        try:
            response = requests.get(f"{self.esp32_url}/status", timeout=5)
            if response.status_code == 200:
                print("✓ ESP32-CAM connection successful.")
                self.esp32_connected = True
                return True
            else:
                print(f"✗ ESP32-CAM responded with status: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"✗ Failed to connect to ESP32-CAM: {e}")
            print("  Please ensure:")
            print("  - Your laptop is connected to the 'ESP32_CAM_DIRECT' Wi-Fi network.")
            print(f"  - The ESP32-CAM IP address is correct (current: {self.esp32_ip}).")
            return False

    def receive_hex_template(self):
        """Receive a hex-encoded fingerprint template from the Arduino."""
        print("Waiting for fingerprint data from sensor...")
        hex_string = ""
        in_hex_block = False
        
        # Wait for the "HEX_START" marker
        while not self.running:
            return None # Stop if main loop is stopped
        
        while True:
            line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"SERIAL IN: {line}") # Debugging line
            if "HEX_START" in line:
                print("HEX_START marker found. Receiving data...")
                in_hex_block = True
                break
            time.sleep(0.01)

        if not in_hex_block:
            return None

        # Read data until "HEX_END" marker is found
        while True:
            line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
            if "HEX_END" in line:
                print("HEX_END marker found. Transmission complete.")
                break
            # Clean the line to ensure it only contains valid hex characters
            clean_line = ''.join(c for c in line.upper() if c in '0123456789ABCDEF')
            hex_string += clean_line
        
        if not hex_string:
            print("✗ No hex data was received.")
            return None

        try:
            # Convert the hex string to binary data
            binary_data = binascii.unhexlify(hex_string)
            print(f"✓ Successfully decoded {len(binary_data)} bytes of fingerprint data.")
            return binary_data
        except binascii.Error as e:
            print(f"✗ Error decoding hex string: {e}")
            return None

    def save_fingerprint_hex(self, template_data, session_id):
        """Saves the fingerprint template data as a formatted .hex file."""
        filepath = os.path.join(self.output_dir, f"{session_id}_fingerprint.hex")
        hex_string = binascii.hexlify(template_data).decode('ascii').upper()
        
        try:
            with open(filepath, 'w') as f:
                f.write(f"# Fingerprint Template for Session: {session_id}\n")
                f.write(f"# Captured on: {datetime.now().isoformat()}\n")
                f.write(f"# Total Bytes: {len(template_data)}\n\n")
                # Write the hex data in a readable format (16 bytes per line)
                for i in range(0, len(hex_string), 32):
                    line = hex_string[i:i+32]
                    formatted_line = ' '.join(line[j:j+2] for j in range(0, len(line), 2))
                    f.write(f"{i//2:08X}: {formatted_line}\n")
            print(f"✓ Fingerprint saved to: {filepath}")
            return filepath
        except IOError as e:
            print(f"✗ Error saving .hex file: {e}")
            return None

    def record_video_stream(self, session_id, duration=10):
        """Records the video stream from the ESP32-CAM."""
        if not self.esp32_connected:
            print("⚠️ Cannot record video, ESP32-CAM is not connected.")
            return None

        video_filepath = os.path.join(self.output_dir, f"{session_id}_video.avi")
        stream_url = f"{self.esp32_url}/stream"
        
        print(f"📹 Starting video recording for {duration} seconds...")
        
        try:
            cap = cv2.VideoCapture(stream_url)
            if not cap.isOpened():
                print(f"✗ Error: Could not open video stream at {stream_url}")
                return None

            # Get frame dimensions from the stream
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = 20.0 # A reasonable default for ESP32-CAM streams
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(video_filepath, fourcc, fps, (frame_width, frame_height))
            
            print(f"Recording at {frame_width}x{frame_height} resolution.")

            start_time = time.time()
            while (time.time() - start_time) < duration:
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
                    # Optional: Display the stream while recording
                    # cv2.imshow('Recording...', frame)
                    # if cv2.waitKey(1) & 0xFF == ord('q'):
                    #     break
                else:
                    print("Warning: Dropped a frame.")
                    time.sleep(0.05)
            
            cap.release()
            out.release()
            # cv2.destroyAllWindows()
            print(f"✓ Video saved to: {video_filepath}")
            return video_filepath

        except Exception as e:
            print(f"✗ An error occurred during video recording: {e}")
            return None
            
    def create_session_info(self, session_id, fingerprint_file, video_file):
        """Creates a JSON file with metadata for the capture session."""
        info_filepath = os.path.join(self.output_dir, f"{session_id}_info.json")
        session_data = {
            "session_id": session_id,
            "capture_timestamp": datetime.now().isoformat(),
            "files": {
                "fingerprint_hex": os.path.basename(fingerprint_file) if fingerprint_file else None,
                "video_avi": os.path.basename(video_file) if video_file else None,
            },
            "status": "complete" if fingerprint_file and video_file else "partial"
        }
        try:
            with open(info_filepath, 'w') as f:
                json.dump(session_data, f, indent=4)
            print(f"✓ Session metadata saved to: {info_filepath}")
        except IOError as e:
            print(f"✗ Error saving session info file: {e}")


    def run(self):
        """The main execution loop for the capture system."""
        print("\n--- Integrated Fingerprint & Video Capture System ---")
        
        # 1. Connect to ESP32-CAM
        if not self.test_esp32_connection():
            if input("Continue without video recording? (y/n): ").lower() != 'y':
                return

        # 2. Connect to Arduino
        if not self.connect_arduino():
            print("💥 Could not connect to Arduino. Exiting.")
            return

        self.running = True
        print("\n✅ System is ready. Place your finger on the sensor to start a capture session.")
        print("Press Ctrl+C to exit.")

        try:
            while self.running:
                # This outer loop waits for the start of a fingerprint transmission
                line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                if "HEX_START" in line:
                    # A session is initiated by the Arduino
                    session_id = self.generate_session_id()
                    print(f"\n{'='*20}\n⚡️ New Capture Session Started: {session_id}\n{'='*20}")
                    
                    # 1. Receive and save fingerprint
                    template_data = self.receive_hex_template_after_start()
                    fingerprint_file = None
                    if template_data:
                        fingerprint_file = self.save_fingerprint_hex(template_data, session_id)
                    else:
                        print("✗ Fingerprint capture failed.")
                        continue # Wait for the next attempt

                    # 2. Record video
                    video_file = self.record_video_stream(session_id, duration=10)

                    # 3. Create metadata file
                    self.create_session_info(session_id, fingerprint_file, video_file)
                    
                    print(f"\n✅ Session {session_id} complete. Ready for next capture.")

                time.sleep(0.1) # Prevent high CPU usage
        except KeyboardInterrupt:
            print("\n🛑 User interrupted. Shutting down.")
        finally:
            self.running = False
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                print("Serial port closed.")
            print("👋 Goodbye!")

    def receive_hex_template_after_start(self):
        """Receives hex data now that the 'HEX_START' is confirmed."""
        hex_string = ""
        while True:
            line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
            if "HEX_END" in line:
                print("HEX_END marker found. Transmission complete.")
                break
            clean_line = ''.join(c for c in line.upper() if c in '0123456789ABCDEF')
            hex_string += clean_line
        
        if not hex_string:
            print("✗ No hex data was received.")
            return None

        try:
            return binascii.unhexlify(hex_string)
        except binascii.Error as e:
            print(f"✗ Error decoding hex string: {e}")
            return None


if __name__ == '__main__':
    # Allow user to specify ESP32-CAM IP address
    default_ip = "192.168.4.1"
    esp32_ip = input(f"Enter ESP32-CAM IP address (default: {default_ip}): ").strip()
    if not esp32_ip:
        esp32_ip = default_ip

    # Create and run the system
    capture_system = IntegratedCaptureSystem(esp32_ip=esp32_ip)
    capture_system.run()
