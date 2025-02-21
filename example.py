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
from tkinter import ttk, scrolledtext

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
        
        ttk.Button(button_frame, text="Encrypt & Send",
                  command=self._encrypt_and_send).pack(side='left', padx=5)
        
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
            
    def _encrypt_and_send(self):
        """Encrypt message and send over network"""
        try:
            # Get message
            message = self.message_text.get('1.0', 'end-1c').encode()
            
            # Encrypt and sign
            ciphertext, nonce, signature = self.hybrid.encrypt_and_sign(
                message, self.private_key)
            
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
                f"\nMessage encrypted and sent to {host}:{port}\n")
            self.output_text.see('end')
            
        except Exception as e:
            self.output_text.insert('end', 
                f"\nError encrypting/sending message: {str(e)}\n")
            
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