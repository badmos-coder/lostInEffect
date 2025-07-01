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
from dilithium.file_operations import FileEncryptionManager
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from datetime import datetime
import os
import threading
import json

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
        
        # Initialize file encryption manager
        self.file_manager = FileEncryptionManager(hybrid)
        
        # Setup GUI
        self._setup_gui()
        
    def _setup_gui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        encryption_tab = ttk.Frame(notebook)
        automated_tab = ttk.Frame(notebook)
        monitoring_tab = ttk.Frame(notebook)
        
        notebook.add(encryption_tab, text='Manual Mode')
        notebook.add(automated_tab, text='Automated Mode')
        notebook.add(monitoring_tab, text='Monitoring')
        
        self._setup_encryption_tab(encryption_tab)
        self._setup_automated_tab(automated_tab)
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
        
    def _setup_automated_tab(self, parent):
        # Create main notebook for different automated operations
        auto_notebook = ttk.Notebook(parent)
        auto_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Message Automation Tab
        message_frame = ttk.Frame(auto_notebook)
        auto_notebook.add(message_frame, text='Message Automation')
        self._setup_message_automation(message_frame)
        
        # File Operations Tab
        folder_frame = ttk.Frame(auto_notebook)
        auto_notebook.add(folder_frame, text='Batch File Operations')
        self._setup_folder_operations(folder_frame)
        
    def _setup_message_automation(self, parent):
        # Auto key generation checkbox
        auto_key_frame = ttk.LabelFrame(parent, text="Auto Key Generation", padding=10)
        auto_key_frame.pack(fill='x', padx=10, pady=5)
        
        self.auto_generate_keys_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(auto_key_frame, text="Automatically generate keys for each operation", 
                       variable=self.auto_generate_keys_var).pack(side='left', padx=5)
        
        # Message frame with auto encryption
        msg_frame = ttk.LabelFrame(parent, text="Auto Encrypt & Send Message", padding=15)
        msg_frame.pack(fill='x', padx=10, pady=5)
        
        self.auto_message_text = tk.Text(msg_frame, height=4)
        self.auto_message_text.pack(fill='x', padx=5, pady=5)
        
        # Auto buttons
        auto_button_frame = ttk.Frame(msg_frame)
        auto_button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(auto_button_frame, text="Auto Encrypt & Store",
                  command=self._auto_encrypt_store_message).pack(side='left', padx=5)
        ttk.Button(auto_button_frame, text="Auto Encrypt & Send",
                  command=self._auto_encrypt_send_message).pack(side='left', padx=5)
        
        # Auto output
        auto_output_frame = ttk.LabelFrame(parent, text="Auto Operation Output", padding=15)
        auto_output_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.auto_message_output = scrolledtext.ScrolledText(auto_output_frame, height=8)
        self.auto_message_output.pack(fill='both', expand=True, padx=5, pady=5)
        
    def _setup_folder_operations(self, parent):
        # Folder selection frame
        folder_frame = ttk.LabelFrame(parent, text="Folder Selection", padding=15)
        folder_frame.pack(fill='x', padx=10, pady=5)
        
        # Input folder selection
        input_folder_frame = ttk.Frame(folder_frame)
        input_folder_frame.pack(fill='x', pady=5)
        
        ttk.Label(input_folder_frame, text="Source Folder (files to encrypt):").pack(side='left', padx=5)
        self.input_folder_var = tk.StringVar(value="No folder selected")
        self.input_folder_label = ttk.Label(input_folder_frame, 
                                          textvariable=self.input_folder_var,
                                          relief='sunken', width=50)
        self.input_folder_label.pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(input_folder_frame, text="Browse...", 
                  command=self._select_input_folder).pack(side='right', padx=5)
        
        # Output folder selection
        output_folder_frame = ttk.Frame(folder_frame)
        output_folder_frame.pack(fill='x', pady=5)
        
        ttk.Label(output_folder_frame, text="Destination Folder (for encrypted files):").pack(side='left', padx=5)
        self.output_folder_var = tk.StringVar(value="No folder selected")
        self.output_folder_label = ttk.Label(output_folder_frame, 
                                           textvariable=self.output_folder_var,
                                           relief='sunken', width=50)
        self.output_folder_label.pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(output_folder_frame, text="Browse...", 
                  command=self._select_output_folder).pack(side='right', padx=5)
        
        # Info frame
        info_frame = ttk.LabelFrame(parent, text="How it works", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        info_text = ("📁 Encrypts each individual file within the selected folder\n"
                    "🔒 Each file becomes a separate .encrypted file\n"
                    "🗂️ Preserves folder structure in the destination\n"
                    "🔑 Automatically generates keys for each operation")
        ttk.Label(info_frame, text=info_text, justify='left').pack(side='left', padx=5)
        
        # Operation buttons
        operation_frame = ttk.Frame(parent)
        operation_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(operation_frame, text="Encrypt All Files in Folder", 
                  command=self._auto_encrypt_folder).pack(side='left', padx=5)
        ttk.Button(operation_frame, text="Decrypt All Files in Folder", 
                  command=self._auto_decrypt_folder).pack(side='left', padx=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(parent, text="Operation Progress", padding=15)
        progress_frame.pack(fill='x', padx=10, pady=5)
        
        self.folder_status_var = tk.StringVar(value="Ready")
        self.folder_status_label = ttk.Label(progress_frame, textvariable=self.folder_status_var)
        self.folder_status_label.pack(side='left', padx=5)
        
        self.folder_progress = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.folder_progress.pack(side='right', padx=5)
        
        # Folder operations output
        folder_output_frame = ttk.LabelFrame(parent, text="Folder Operation Output", padding=15)
        folder_output_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.folder_output_text = scrolledtext.ScrolledText(folder_output_frame, height=8)
        self.folder_output_text.pack(fill='both', expand=True, padx=5, pady=5)
        
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
    
    # New automated methods for file and folder operations
    def _auto_encrypt_store_message(self):
        """Auto encrypt message and store locally"""
        try:
            message = self.auto_message_text.get('1.0', 'end-1c').encode()
            
            if not message.strip():
                messagebox.showwarning("Empty Message", "Please enter a message to encrypt.")
                return
            
            # Auto generate keys if enabled
            if self.auto_generate_keys_var.get():
                self.auto_message_output.insert('end', "Auto-generating keys...\n")
                self.public_key, self.private_key = self.hybrid.generate_keys()
                self.auto_message_output.insert('end', "Keys generated successfully!\n")
            elif not hasattr(self, 'private_key'):
                messagebox.showwarning("No Keys", "Please generate keys first or enable auto-generation.")
                return
            
            # Encrypt message
            self.auto_message_output.insert('end', f"Encrypting message ({len(message)} bytes)...\n")
            start_time = datetime.now()
            ciphertext, nonce, signature = self.hybrid.encrypt_and_sign(message, self.private_key)
            end_time = datetime.now()
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"encrypted_message_{timestamp}.json"
            
            encrypted_data = {
                'ciphertext': ciphertext.hex(),
                'nonce': nonce.hex(),
                'signature': {
                    'mu': signature[0].hex(),
                    'z': signature[1].tolist()
                },
                'public_key': {
                    'seed': self.public_key['seed'].hex(),
                    't': self.public_key['t'].tolist()
                },
                'encrypted_at': datetime.now().isoformat(),
                'message_size': len(message)
            }
            
            with open(filename, 'w') as f:
                json.dump(encrypted_data, f, indent=2)
            
            self.auto_message_output.insert('end', 
                f"Message encrypted and saved to '{filename}' in {(end_time-start_time).total_seconds():.3f}s\n")
            self.auto_message_output.insert('end', f"Ciphertext size: {len(ciphertext)} bytes\n\n")
            self.auto_message_output.see('end')
            
        except Exception as e:
            self.auto_message_output.insert('end', f"Error: {str(e)}\n")
            
    def _auto_encrypt_send_message(self):
        """Auto encrypt message and send over network"""
        try:
            message = self.auto_message_text.get('1.0', 'end-1c').encode()
            
            if not message.strip():
                messagebox.showwarning("Empty Message", "Please enter a message to send.")
                return
            
            # Auto generate keys if enabled
            if self.auto_generate_keys_var.get():
                self.auto_message_output.insert('end', "Auto-generating keys...\n")
                self.public_key, self.private_key = self.hybrid.generate_keys()
                self.auto_message_output.insert('end', "Keys generated successfully!\n")
            elif not hasattr(self, 'private_key'):
                messagebox.showwarning("No Keys", "Please generate keys first or enable auto-generation.")
                return
            
            # Encrypt and send
            self.auto_message_output.insert('end', f"Auto-encrypting and sending message ({len(message)} bytes)...\n")
            start_time = datetime.now()
            ciphertext, nonce, signature = self.hybrid.encrypt_and_sign(message, self.private_key)
            end_time = datetime.now()
            
            self.auto_message_output.insert('end',
                f"Encryption completed in {(end_time-start_time).total_seconds():.3f} seconds\n")
            self.auto_message_output.insert('end',
                f"Ciphertext size: {len(ciphertext)} bytes\n")
            
            # Send over network
            host = self.host_entry.get() or 'localhost'
            port = int(self.port_entry.get() or '5000')
            
            # Pack and send message
            message_data = self.protocol.pack_message(
                ciphertext, nonce, signature, self.public_key)
            self.sender.send_message(message_data)
            
            self.auto_message_output.insert('end', f"Message sent successfully to {host}:{port}\n\n")
            self.auto_message_output.see('end')
            
        except Exception as e:
            self.auto_message_output.insert('end', f"Error: {str(e)}\n")
    
    def _select_input_folder(self):
        """Select input folder for encryption"""
        folder_path = filedialog.askdirectory(title="Select Input Folder")
        if folder_path:
            self.selected_input_folder = folder_path
            folder_name = os.path.basename(folder_path)
            self.input_folder_var.set(f"{folder_name} ({folder_path})")
            
            # Count files in folder
            files = self.file_manager.get_files_in_folder(folder_path)
            self.folder_output_text.insert('end', f"Selected input folder: {folder_path}\n")
            self.folder_output_text.insert('end', f"Found {len(files)} files to process\n\n")
        else:
            self.selected_input_folder = None
            self.input_folder_var.set("No folder selected")
    
    def _select_output_folder(self):
        """Select output folder for encrypted files"""
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:
            self.selected_output_folder = folder_path
            folder_name = os.path.basename(folder_path)
            self.output_folder_var.set(f"{folder_name} ({folder_path})")
            self.folder_output_text.insert('end', f"Selected output folder: {folder_path}\n\n")
        else:
            self.selected_output_folder = None
            self.output_folder_var.set("No folder selected")
    
    def _auto_encrypt_folder(self):
        """Auto encrypt entire folder with automatic key generation"""
        try:
            if not hasattr(self, 'selected_input_folder') or not self.selected_input_folder:
                messagebox.showwarning("No Input Folder", "Please select an input folder first.")
                return
            
            if not hasattr(self, 'selected_output_folder') or not self.selected_output_folder:
                messagebox.showwarning("No Output Folder", "Please select an output folder first.")
                return
            
            # Setup progress callbacks
            self.file_manager.set_callbacks(
                lambda value: self.folder_progress.configure(value=value),
                lambda message: self.folder_status_var.set(message)
            )
            
            def run_encryption():
                try:
                    self.folder_output_text.insert('end', "=== Starting Individual File Encryption ===\n")
                    self.folder_output_text.insert('end', f"Source folder: {self.selected_input_folder}\n")
                    self.folder_output_text.insert('end', f"Destination folder: {self.selected_output_folder}\n")
                    self.folder_output_text.insert('end', "Processing: Each file will be encrypted separately\n\n")
                    self.folder_output_text.see('end')
                    
                    result = self.file_manager.encrypt_folder(
                        self.selected_input_folder, 
                        self.selected_output_folder, 
                        auto_generate_keys=True
                    )
                    
                    if result['status'] == 'success':
                        self.folder_output_text.insert('end', "\n=== Encryption Summary ===\n")
                        self.folder_output_text.insert('end', f"Total files: {result['total_files']}\n")
                        self.folder_output_text.insert('end', f"Successfully encrypted: {result['successful']}\n")
                        self.folder_output_text.insert('end', f"Failed: {result['failed']}\n")
                        self.folder_output_text.insert('end', f"Summary saved to: {result['summary_file']}\n")
                    else:
                        self.folder_output_text.insert('end', f"\nEncryption failed: {result['error']}\n")
                    
                    self.folder_output_text.see('end')
                    
                except Exception as e:
                    self.folder_output_text.insert('end', f"\nError during encryption: {str(e)}\n")
                    self.folder_status_var.set("Error")
            
            # Run in separate thread
            threading.Thread(target=run_encryption, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Encryption Error", f"Error starting encryption: {str(e)}")
    
    def _auto_decrypt_folder(self):
        """Auto decrypt entire folder of encrypted files"""
        try:
            if not hasattr(self, 'selected_input_folder') or not self.selected_input_folder:
                messagebox.showwarning("No Input Folder", "Please select an input folder with encrypted files first.")
                return
            
            if not hasattr(self, 'selected_output_folder') or not self.selected_output_folder:
                messagebox.showwarning("No Output Folder", "Please select an output folder for decrypted files first.")
                return
            
            # Setup progress callbacks
            self.file_manager.set_callbacks(
                lambda value: self.folder_progress.configure(value=value),
                lambda message: self.folder_status_var.set(message)
            )
            
            def run_decryption():
                try:
                    self.folder_output_text.insert('end', "=== Starting Individual File Decryption ===\n")
                    self.folder_output_text.insert('end', f"Source folder: {self.selected_input_folder}\n")
                    self.folder_output_text.insert('end', f"Destination folder: {self.selected_output_folder}\n")
                    self.folder_output_text.insert('end', "Processing: Each .encrypted file will be decrypted separately\n\n")
                    self.folder_output_text.see('end')
                    
                    result = self.file_manager.decrypt_folder(
                        self.selected_input_folder, 
                        self.selected_output_folder
                    )
                    
                    if result['status'] == 'success':
                        self.folder_output_text.insert('end', "\n=== Decryption Summary ===\n")
                        self.folder_output_text.insert('end', f"Total encrypted files: {result['total_files']}\n")
                        self.folder_output_text.insert('end', f"Successfully decrypted: {result['successful']}\n")
                        self.folder_output_text.insert('end', f"Failed: {result['failed']}\n")
                    else:
                        self.folder_output_text.insert('end', f"\nDecryption failed: {result['error']}\n")
                    
                    self.folder_output_text.see('end')
                    
                except Exception as e:
                    self.folder_output_text.insert('end', f"\nError during decryption: {str(e)}\n")
                    self.folder_status_var.set("Error")
            
            # Run in separate thread
            threading.Thread(target=run_decryption, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Decryption Error", f"Error starting decryption: {str(e)}")
            
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