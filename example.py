from dilithium.core import DilithiumParams
from dilithium.keygen import KeyGenerator
from dilithium.sign import Signer
from dilithium.verify import Verifier
import time
import numpy as np
from dilithium.chaos import HybridEncryption
from dilithium.monitoring.metrics import MonitoringSystem
from dilithium.monitoring.health import HealthCheck
from dilithium.config import SecurityConfig
from dilithium.network.protocol import CryptoNetworkProtocol, MessageSender
from dilithium.security.audit import SecureAuditLog
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from datetime import datetime
import os

class DilithiumGUI:
    def __init__(self, hybrid: HybridEncryption, monitoring: MonitoringSystem, health: HealthCheck):
        self.root = tk.Tk()
        self.root.title("Quantum-Resistant Cryptography System")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.hybrid = hybrid
        self.monitoring = monitoring
        self.health = health
        self.config = SecurityConfig()
        self.audit_log = SecureAuditLog(self.config)
        
        # Add network components
        self.protocol = CryptoNetworkProtocol(self.audit_log)
        self.sender = MessageSender(self.protocol)
        
        # Setup GUI
        self._setup_gui()
        
    def _setup_gui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        encryption_tab = ttk.Frame(notebook)
        monitoring_tab = ttk.Frame(notebook)
        
        notebook.add(encryption_tab, text='Encryption')
        notebook.add(monitoring_tab, text='Monitoring')
        
        self._setup_encryption_tab(encryption_tab)
        self._setup_monitoring_tab(monitoring_tab)
        
    def _setup_encryption_tab(self, parent):
        # Key generation frame
        key_frame = ttk.LabelFrame(parent, text="Key Generation", padding=15)
        key_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(key_frame, text="Generate Keys",
                  command=self._generate_keys).pack(side='left', padx=5)
        
        # Message frame
        msg_frame = ttk.LabelFrame(parent, text="Message", padding=15)
        msg_frame.pack(fill='x', padx=10, pady=5)
        
        self.message_text = tk.Text(msg_frame, height=4)
        self.message_text.pack(fill='x', padx=5, pady=5)
        
        # File selection frame
        file_frame = ttk.LabelFrame(parent, text="File Selection", padding=15)
        file_frame.pack(fill='x', padx=10, pady=5)
        
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(file_select_frame, text="Select File",
                  command=self._select_file).pack(side='left', padx=5)
        
        self.file_path_var = tk.StringVar(value="No file selected")
        ttk.Label(file_select_frame, textvariable=self.file_path_var,
                 relief='sunken', width=60).pack(side='left', padx=5, fill='x', expand=True)
        
        # Network frame
        network_frame = ttk.LabelFrame(parent, text="Network Transmission", padding=15)
        network_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(network_frame, text="Receiver Host:").pack(side='left', padx=5)
        self.host_entry = ttk.Entry(network_frame, width=20)
        self.host_entry.insert(0, 'localhost')
        self.host_entry.pack(side='left', padx=5)
        
        ttk.Label(network_frame, text="Port:").pack(side='left', padx=5)
        self.port_entry = ttk.Entry(network_frame, width=8)
        self.port_entry.insert(0, '5000')
        self.port_entry.pack(side='left', padx=5)
        
        # Action buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(button_frame, text="Encrypt & Send Message",
                  command=self._encrypt_and_send_message).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Encrypt & Send File",
                  command=self._encrypt_and_send_file).pack(side='left', padx=5)
        
        # Output frame
        output_frame = ttk.LabelFrame(parent, text="Output", padding=15)
        output_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=10)
        self.output_text.pack(fill='both', expand=True, padx=5, pady=5)
        
    def _setup_monitoring_tab(self, parent):
        # Add monitoring widgets
        status_frame = ttk.LabelFrame(parent, text="System Status", padding=15)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=15)
        self.status_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        self._update_status()
        
    def _generate_keys(self):
        """Generate new key pair"""
        try:
            self.public_key, self.private_key = self.hybrid.generate_keys()
            self.output_text.insert('end', "\nKeys generated successfully\n")
            self._print_key("Public Key", self.public_key)
            self.output_text.see('end')
        except Exception as e:
            self.output_text.insert('end', f"\nError generating keys: {str(e)}\n")
            
    def _select_file(self):
        """Select a file for encryption and transmission"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select file to encrypt and send",
                filetypes=[
                    ("All files", "*.*"),
                    ("Text files", "*.txt"),
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("Document files", "*.pdf *.doc *.docx"),
                    ("Archive files", "*.zip *.rar *.7z")
                ]
            )
            
            if file_path:
                self.selected_file_path = file_path
                filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                self.file_path_var.set(f"{filename} ({file_size:,} bytes)")
                
                self.output_text.insert('end', 
                    f"\nSelected file: {filename}\n")
                self.output_text.insert('end', 
                    f"File size: {file_size:,} bytes\n")
            else:
                self.selected_file_path = None
                self.file_path_var.set("No file selected")
                
        except Exception as e:
            messagebox.showerror("File Selection Error", f"Error selecting file: {str(e)}")
            
    def _encrypt_and_send_message(self):
        """Encrypt message and send over network"""
        try:
            # Check if keys are generated
            if not hasattr(self, 'private_key') or not self.private_key:
                messagebox.showwarning("No Keys", "Please generate keys first.")
                return
                
            # Get message
            message = self.message_text.get('1.0', 'end-1c').encode()
            
            if not message.strip():
                messagebox.showwarning("Empty Message", "Please enter a message to send.")
                return
            
            self.output_text.insert('end', 
                f"\nStarting encryption process for message of size {len(message)} bytes...\n")
            
            # Encrypt and sign
            start_time = datetime.now()
            ciphertext, nonce, signature = self.hybrid.encrypt_and_sign(
                message, self.private_key)
            end_time = datetime.now()
            
            self.output_text.insert('end',
                f"Encryption completed in {(end_time-start_time).total_seconds():.3f} seconds\n")
            self.output_text.insert('end',
                f"Ciphertext size: {len(ciphertext)} bytes\n")
            
            # Verify encryption worked
            try:
                decrypted = self.hybrid.verify_and_decrypt(
                    ciphertext, nonce, signature, self.public_key)
                if decrypted != message:
                    raise ValueError("Encryption verification failed")
                self.output_text.insert('end', "Encryption verified successfully\n")
            except Exception as e:
                raise ValueError(f"Encryption verification failed: {str(e)}")
            
            # Get network settings
            host = self.host_entry.get()
            port = int(self.port_entry.get())
            
            # Update sender configuration
            self.sender.host = host
            self.sender.port = port
            
            # Pack and send message
            message_data = self.protocol.pack_message(
                ciphertext, nonce, signature, self.public_key)
            self.sender.send_message(message_data)
            
            self.output_text.insert('end', 
                f"Message encrypted and sent to {host}:{port}\n")
            self.output_text.see('end')
            
        except Exception as e:
            self.output_text.insert('end', 
                f"\nError encrypting/sending message: {str(e)}\n")
                
    def _encrypt_and_send_file(self):
        """Encrypt file and send over network"""
        try:
            # Check if file is selected
            if not hasattr(self, 'selected_file_path') or not self.selected_file_path:
                messagebox.showwarning("No File Selected", "Please select a file to encrypt and send.")
                return
                
            # Check if keys are generated
            if not hasattr(self, 'private_key') or not self.private_key:
                messagebox.showwarning("No Keys", "Please generate keys first.")
                return
            
            # Read file
            with open(self.selected_file_path, 'rb') as f:
                file_data = f.read()
            
            filename = os.path.basename(self.selected_file_path)
            file_size = len(file_data)
            
            self.output_text.insert('end', 
                f"\nStarting encryption process for file '{filename}' ({file_size:,} bytes)...\n")
            
            # Encrypt and sign file data
            start_time = datetime.now()
            ciphertext, nonce, signature = self.hybrid.encrypt_and_sign(
                file_data, self.private_key)
            end_time = datetime.now()
            
            self.output_text.insert('end',
                f"File encryption completed in {(end_time-start_time).total_seconds():.3f} seconds\n")
            self.output_text.insert('end',
                f"Encrypted file size: {len(ciphertext)} bytes\n")
            
            # Verify encryption worked
            try:
                decrypted = self.hybrid.verify_and_decrypt(
                    ciphertext, nonce, signature, self.public_key)
                if decrypted != file_data:
                    raise ValueError("File encryption verification failed")
                self.output_text.insert('end', "File encryption verified successfully\n")
            except Exception as e:
                raise ValueError(f"File encryption verification failed: {str(e)}")
            
            # Get network settings
            host = self.host_entry.get()
            port = int(self.port_entry.get())
            
            # Update sender configuration
            self.sender.host = host
            self.sender.port = port
            
            # Pack and send file
            file_message_data = self.protocol.pack_file(
                ciphertext, nonce, signature, self.public_key,
                filename, file_size, os.path.splitext(filename)[1])
            self.sender.send_message(file_message_data)
            
            self.output_text.insert('end', 
                f"File '{filename}' encrypted and sent to {host}:{port}\n")
            self.output_text.see('end')
            
        except FileNotFoundError:
            messagebox.showerror("File Error", "Selected file not found. Please select a valid file.")
        except PermissionError:
            messagebox.showerror("Permission Error", "Permission denied reading the file.")
        except Exception as e:
            self.output_text.insert('end', 
                f"\nError encrypting/sending file: {str(e)}\n")
            messagebox.showerror("Encryption Error", f"Error encrypting/sending file: {str(e)}")
            
    def _update_status(self):
        """Update monitoring status"""
        if hasattr(self, 'status_text'):
            status = self.health.get_health_report()
            self.status_text.delete('1.0', 'end')
            self.status_text.insert('end', f"System Status: {status['status']}\n\n")
            self.status_text.insert('end', "Performance Metrics:\n")
            for metric, value in status['metrics'].items():
                self.status_text.insert('end', f"{metric}: {value}\n")
            
            self.root.after(5000, self._update_status)  # Update every 5 seconds
            
    def _print_key(self, name: str, key: dict):
        """Print key details to output"""
        self.output_text.insert('end', f"\n{name}:")
        for k, v in key.items():
            if isinstance(v, np.ndarray):
                self.output_text.insert('end', 
                    f"\n  {k}: array of shape {v.shape}, first few values: {v.flatten()[:5]}")
            else:
                val_str = f"{v[:20]}..." if isinstance(v, bytes) else f"{v}"
                self.output_text.insert('end', f"\n  {k}: {val_str}")
                
    def _handle_message(self, message_components):
        """Handle received message with detailed decryption process"""
        try:
            # Unpack components
            ciphertext, nonce, signature, public_key = message_components
            
            # Log decryption process
            self.process_text.insert('end', 
                f"\n[{datetime.now()}] Starting decryption process:\n")
            
            # Log signature verification
            self.process_text.insert('end', "\n1. Verifying signature...\n")
            self.process_text.insert('end', f"   Signature size: {len(signature[0])} bytes\n")
            self.process_text.insert('end', f"   Public key components: {list(public_key.keys())}\n")
            
            # Log decryption
            self.process_text.insert('end', "\n2. Decrypting message...\n")
            self.process_text.insert('end', f"   Ciphertext size: {len(ciphertext)} bytes\n")
            self.process_text.insert('end', f"   Nonce size: {len(nonce)} bytes\n")
            
            # Perform decryption
            start_time = datetime.now()
            decrypted = self.hybrid.verify_and_decrypt(
                ciphertext, nonce, signature, public_key)
            end_time = datetime.now()
            
            # Update message count and average time
            process_time = (end_time - start_time).total_seconds()
            self._message_count += 1
            self._avg_time = ((self._avg_time * (self._message_count - 1)) + 
                            process_time) / self._message_count
            
            # Log completion
            self.process_text.insert('end', "\n3. Decryption completed successfully\n")
            self.process_text.insert('end', 
                f"   Time taken: {process_time:.3f} seconds\n")
            self.process_text.insert('end',
                f"   Original message size: {len(decrypted)} bytes\n")
            
            # Update statistics
            self.stats_text.delete('1.0', 'end')
            self.stats_text.insert('end', "Decryption Statistics:\n")
            self.stats_text.insert('end', 
                f"Messages processed: {self._message_count}\n")
            self.stats_text.insert('end',
                f"Average processing time: {self._avg_time:.3f} seconds\n")
            self.stats_text.insert('end',
                f"Last message size: {len(decrypted)} bytes\n")
            
            # Display decrypted message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.message_text.insert('end', 
                f"\n[{timestamp}] Received message:\n{decrypted.decode()}\n")
            self.message_text.see('end')
            
            self.status_var.set("Message received and decrypted successfully")
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            self.status_var.set(error_msg)
            self.process_text.insert('end', f"\nError: {error_msg}\n")
            
        finally:
            # Auto-scroll process log
            self.process_text.see('end')
            
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

def main():
    # Initialize components
    config = SecurityConfig()
    params = DilithiumParams.get_params(security_level=3)
    hybrid = HybridEncryption(params)
    
    # Setup monitoring
    monitoring = MonitoringSystem(config)
    health = HealthCheck(config, monitoring)
    
    # Launch GUI
    gui = DilithiumGUI(hybrid, monitoring, health)
    gui.run()

if __name__ == "__main__":
    main() 