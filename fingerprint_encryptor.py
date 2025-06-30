#!/usr/bin/env python3
"""
Fixed Fingerprint Template Receiver
Receives fingerprint templates from Arduino via USB serial
with improved error handling and timeout management.
"""

import serial
import serial.tools.list_ports
import time
import os
from datetime import datetime
import sys
import binascii

class FingerprintReceiver:
    def __init__(self, baudrate=115200, output_dir="fingerprint_templates"):
        self.baudrate = baudrate
        self.output_dir = output_dir
        self.serial_port = None
        self.running = False
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}")
    
    def find_arduino_port(self):
        """Automatically detect Arduino port"""
        ports = serial.tools.list_ports.comports()
        arduino_ports = []
        
        for port in ports:
            # Look for common Arduino/ESP32 identifiers
            description = port.description.lower()
            if any(keyword in description for keyword in 
                   ['arduino', 'ch340', 'cp210', 'ftdi', 'usb serial', 'esp32', 'esp8266']):
                arduino_ports.append(port.device)
        
        if arduino_ports:
            print(f"Found potential Arduino/ESP32 ports: {arduino_ports}")
            return arduino_ports[0]
        
        return None
    
    def list_available_ports(self):
        """List all available serial ports"""
        ports = serial.tools.list_ports.comports()
        print("\nAvailable serial ports:")
        for i, port in enumerate(ports):
            print(f"{i+1}. {port.device} - {port.description}")
        return [port.device for port in ports]
    
    def connect(self, port=None):
        """Connect to Arduino via serial port"""
        if port is None:
            port = self.find_arduino_port()
        
        if port is None:
            print("No Arduino port found automatically.")
            available_ports = self.list_available_ports()
            
            if not available_ports:
                print("No serial ports available!")
                return False
            
            try:
                choice = int(input("Select port number: ")) - 1
                if 0 <= choice < len(available_ports):
                    port = available_ports[choice]
                else:
                    print("Invalid selection!")
                    return False
            except ValueError:
                print("Invalid input!")
                return False
        
        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            print(f"Connected to {port} at {self.baudrate} baud")
            time.sleep(2)  # Wait for Arduino to reset
            
            # Clear any pending data
            self.serial_port.flushInput()
            self.serial_port.flushOutput()
            
            return True
            
        except serial.SerialException as e:
            print(f"Failed to connect to {port}: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("Serial connection closed")
    
    def read_line_with_timeout(self, timeout=10):
        """Read a complete line with timeout"""
        start_time = time.time()
        line = ""
        
        while (time.time() - start_time) < timeout:
            if self.serial_port.in_waiting > 0:
                try:
                    char = self.serial_port.read(1).decode('utf-8', errors='ignore')
                    if char == '\n':
                        return line.strip()
                    elif char != '\r':
                        line += char
                except UnicodeDecodeError:
                    continue
            time.sleep(0.01)
        
        return None
    
    def save_template(self, template_data, identifier=""):
        """Save template data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"fingerprint_{timestamp}{identifier}"
        
        # Save binary file
        bin_filepath = os.path.join(self.output_dir, f"{base_filename}.bin")
        try:
            with open(bin_filepath, 'wb') as f:
                f.write(template_data)
            print(f"✓ Binary template saved: {bin_filepath} ({len(template_data)} bytes)")
        except Exception as e:
            print(f"✗ Error saving binary file: {e}")
            return None
        
        # Save hex dump for analysis
        hex_filepath = os.path.join(self.output_dir, f"{base_filename}.hex")
        try:
            with open(hex_filepath, 'w') as f:
                hex_data = binascii.hexlify(template_data).decode('ascii').upper()
                # Format as readable hex dump (32 bytes per line)
                for i in range(0, len(hex_data), 64):  # 64 hex chars = 32 bytes
                    line = hex_data[i:i+64]
                    # Add spaces between bytes
                    formatted_line = ' '.join(line[j:j+2] for j in range(0, len(line), 2))
                    f.write(f"{i//2:04X}: {formatted_line}\n")
            print(f"✓ Hex dump saved: {hex_filepath}")
        except Exception as e:
            print(f"✗ Error saving hex file: {e}")
        
        # Save analysis info
        info_filepath = os.path.join(self.output_dir, f"{base_filename}_info.txt")
        try:
            with open(info_filepath, 'w') as f:
                f.write(f"Fingerprint Template Analysis\n")
                f.write(f"=============================\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Template Size: {len(template_data)} bytes\n")
                f.write(f"Binary File: {base_filename}.bin\n")
                f.write(f"Hex Dump: {base_filename}.hex\n\n")
                
                # Basic analysis
                f.write(f"First 32 bytes (hex): {binascii.hexlify(template_data[:32]).decode().upper()}\n")
                f.write(f"Last 32 bytes (hex): {binascii.hexlify(template_data[-32:]).decode().upper()}\n")
                
                # Byte distribution
                byte_counts = {}
                for byte in template_data:
                    byte_counts[byte] = byte_counts.get(byte, 0) + 1
                
                f.write(f"\nByte Statistics:\n")
                f.write(f"Unique bytes: {len(byte_counts)}\n")
                f.write(f"Most common byte: 0x{max(byte_counts, key=byte_counts.get):02X} ({byte_counts[max(byte_counts, key=byte_counts.get)]} times)\n")
                f.write(f"Zero bytes: {byte_counts.get(0, 0)}\n")
                f.write(f"Non-zero bytes: {len(template_data) - byte_counts.get(0, 0)}\n")
                
            print(f"✓ Analysis saved: {info_filepath}")
        except Exception as e:
            print(f"✗ Error saving analysis: {e}")
        
        return bin_filepath
    
    def receive_hex_template(self):
        """Receive hex-encoded template with improved timeout handling"""
        print("📥 Receiving hex-encoded template...")
        hex_data = ""
        timeout = 45  # Increased timeout
        start_time = time.time()
        last_data_time = start_time
        lines_received = 0
        
        while (time.time() - start_time) < timeout:
            line = self.read_line_with_timeout(timeout=2)
            
            if line is None:
                # Check if we haven't received data for too long
                if (time.time() - last_data_time) > 10:
                    print(f"⚠️  No data received for 10 seconds, stopping...")
                    break
                continue
            
            last_data_time = time.time()
            lines_received += 1
            
            # Check for end marker
            if line.strip().upper() in ["HEX_END", "END"]:
                print(f"📤 End marker received after {lines_received} lines")
                break
            
            # Clean hex data (remove non-hex characters)
            clean_line = ''.join(c for c in line.upper() if c in '0123456789ABCDEF')
            
            if clean_line:
                hex_data += clean_line
                print(f"📝 Line {lines_received:2d}: {clean_line[:50]}{'...' if len(clean_line) > 50 else ''} ({len(clean_line)} chars)")
            else:
                print(f"⚠️  Skipping invalid line: {line[:50]}")
        
        print(f"\n📊 Reception Summary:")
        print(f"   Lines received: {lines_received}")
        print(f"   Hex characters: {len(hex_data)}")
        print(f"   Expected bytes: {len(hex_data) // 2}")
        
        if len(hex_data) < 100:  # Minimum threshold
            print(f"✗ Insufficient hex data received")
            return None
        
        try:
            # Convert hex string to binary data
            template_data = binascii.unhexlify(hex_data)
            print(f"✓ Successfully converted to {len(template_data)} bytes")
            return template_data
        except (ValueError, binascii.Error) as e:
            print(f"✗ Error decoding hex data: {e}")
            print(f"   First 100 hex chars: {hex_data[:100]}")
            return None
    
    def listen_for_templates(self):
        """Main listening loop with improved error handling"""
        if not self.serial_port or not self.serial_port.is_open:
            print("Serial port not connected!")
            return
        
        print("🎧 Listening for fingerprint templates...")
        print("   Expecting HEX_START/HEX_END or START/END transmission")
        print("   Press Ctrl+C to stop\n")
        
        self.running = True
        template_count = 0
        
        try:
            while self.running:
                # Read serial data line by line
                line = self.read_line_with_timeout(timeout=3)
                
                if line is None:
                    # Print a heartbeat every 30 seconds
                    if int(time.time()) % 30 == 0:
                        print("💓 Waiting for data...")
                        time.sleep(1)
                    continue
                
                print(f"📨 Received: {line}")
                
                # Check for hex-encoded transmission
                if line.strip().upper() in ["HEX_START"]:
                    template_count += 1
                    print(f"\n🔄 Template #{template_count} - Hex transmission started")
                    
                    template_data = self.receive_hex_template()
                    
                    if template_data:
                        size = len(template_data)
                        print(f"📦 Received template: {size} bytes")
                        
                        if size >= 10:  # Accept any reasonable amount of data
                            filepath = self.save_template(template_data, f"_{template_count:03d}")
                            if filepath:
                                print(f"🎉 Template #{template_count} saved successfully!")
                                print(f"   Size: {size} bytes")
                                print(f"   File: {os.path.basename(filepath)}")
                                
                                if size < 512:
                                    print(f"   ⚠️  Template smaller than expected 512 bytes")
                                    print(f"   This may be partial data or a different format")
                            else:
                                print(f"💥 Failed to save template #{template_count}")
                        else:
                            print(f"⚠️  Template #{template_count} too small: {size} bytes")
                            # Save anyway for debugging
                            filepath = self.save_template(template_data, f"_{template_count:03d}_tiny")
                            if filepath:
                                print(f"🔍 Saved tiny template for analysis: {os.path.basename(filepath)}")
                    else:
                        print(f"💥 Failed to receive template #{template_count}")
                    
                    print(f"\n{'='*50}")
                    print(f"Ready for next template...")
                
                # Check for binary transmission (if needed)
                elif line.strip().upper() in ["START"]:
                    print("⚠️  Binary transmission mode not fully implemented")
                    print("   Please use HEX mode in Arduino code")
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Stopping... (Received {template_count} templates)")
            self.running = False
        except Exception as e:
            print(f"💥 Error in listening loop: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Main application loop"""
        print("🔬 R307 Fingerprint Template Receiver v2.0")
        print("==========================================")
        print("Captures fingerprint templates from Arduino/ESP32")
        print("Supports hex-encoded transmission mode\n")
        
        # Connect to Arduino
        if not self.connect():
            print("💥 Failed to establish connection. Exiting.")
            return
        
        try:
            # Start listening for templates
            self.listen_for_templates()
        finally:
            # Clean up
            self.disconnect()
            print("👋 Goodbye!")

def main():
    print("Starting Fingerprint Template Receiver...")
    
    # Create receiver instance
    receiver = FingerprintReceiver(
        baudrate=115200,
        output_dir="fingerprint_templates"
    )
    
    # Run the application
    receiver.run()

if __name__ == "__main__":
    main()