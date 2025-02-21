import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, Tuple
import threading
from datetime import datetime
from .network.protocol import CryptoNetworkProtocol, MessageReceiver
from .security.audit import SecureAuditLog, AuditEvent
from .monitoring.health import HealthCheck
from .monitoring.metrics import MonitoringSystem
from .config import SecurityConfig
from .chaos import HybridEncryption
from .core import DilithiumParams

class ReceiverGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quantum-Resistant Message Receiver")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.config = SecurityConfig()
        self.params = DilithiumParams.get_params(security_level=3)
        self.hybrid = HybridEncryption(self.params)
        self.audit_log = SecureAuditLog(self.config)
        self.monitoring = MonitoringSystem(self.config)
        self.health = HealthCheck(self.config, self.monitoring)
        
        # Setup network protocol
        self.protocol = CryptoNetworkProtocol(self.audit_log)
        self.receiver = MessageReceiver(self.protocol)
        
        self._setup_gui()
        self._start_receiver()
        
    def _setup_gui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self.messages_tab = ttk.Frame(self.notebook)
        self.decryption_tab = ttk.Frame(self.notebook)
        self.monitoring_tab = ttk.Frame(self.notebook)
        self.logs_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.messages_tab, text='Messages')
        self.notebook.add(self.decryption_tab, text='Decryption Process')
        self.notebook.add(self.monitoring_tab, text='System Monitoring')
        self.notebook.add(self.logs_tab, text='Audit Logs')
        
        self._setup_messages_tab()
        self._setup_decryption_tab()
        self._setup_monitoring_tab()
        self._setup_logs_tab()
        
    def _setup_messages_tab(self):
        # Status frame
        status_frame = ttk.LabelFrame(self.messages_tab, text="Receiver Status")
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_var = tk.StringVar(value="Waiting for messages...")
        ttk.Label(status_frame, 
                 textvariable=self.status_var,
                 font=('Helvetica', 10)).pack(padx=5, pady=5)
        
        # Message display
        msg_frame = ttk.LabelFrame(self.messages_tab, text="Received Messages")
        msg_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.message_text = scrolledtext.ScrolledText(
            msg_frame, height=20, font=('Courier', 10))
        self.message_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(self.messages_tab)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(button_frame, text="Clear Messages",
                  command=self._clear_messages).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Stop Receiver",
                  command=self._stop_receiver).pack(side='left', padx=5)
                  
    def _setup_decryption_tab(self):
        # Decryption process display
        process_frame = ttk.LabelFrame(self.decryption_tab, 
                                     text="Decryption Process Log")
        process_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.process_text = scrolledtext.ScrolledText(
            process_frame, height=30, font=('Courier', 10))
        self.process_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(self.decryption_tab, 
                                   text="Decryption Statistics")
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        self.stats_text = scrolledtext.ScrolledText(
            stats_frame, height=5, font=('Courier', 10))
        self.stats_text.pack(fill='both', expand=True, padx=5, pady=5)
        
    def _setup_monitoring_tab(self):
        # System status
        status_frame = ttk.LabelFrame(self.monitoring_tab, 
                                    text="System Status")
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.system_status = scrolledtext.ScrolledText(
            status_frame, height=10, font=('Courier', 10))
        self.system_status.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Performance metrics
        metrics_frame = ttk.LabelFrame(self.monitoring_tab, 
                                     text="Performance Metrics")
        metrics_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.metrics_text = scrolledtext.ScrolledText(
            metrics_frame, height=15, font=('Courier', 10))
        self.metrics_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Start monitoring updates
        self._update_monitoring()
        
    def _setup_logs_tab(self):
        # Audit log display
        log_frame = ttk.LabelFrame(self.logs_tab, text="System Audit Logs")
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=30, font=('Courier', 10))
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(self.logs_tab)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(button_frame, text="Clear Logs",
                  command=self._clear_logs).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Export Logs",
                  command=self._export_logs).pack(side='left', padx=5)
                  
    def _update_monitoring(self):
        """Update monitoring information"""
        try:
            # Update system status
            health_report = self.health.get_health_report()
            self.system_status.delete('1.0', 'end')
            self.system_status.insert('end', 
                f"System Status: {health_report['status']}\n")
            self.system_status.insert('end', 
                f"Last Check: {datetime.fromtimestamp(health_report['last_check'])}\n")
            self.system_status.insert('end', "\nSystem Information:\n")
            for key, value in health_report['system_info'].items():
                self.system_status.insert('end', f"{key}: {value}\n")
            
            # Update metrics
            metrics = self.monitoring.get_statistics()
            self.metrics_text.delete('1.0', 'end')
            self.metrics_text.insert('end', "Performance Metrics:\n\n")
            for metric_type, values in metrics.items():
                self.metrics_text.insert('end', f"{metric_type}:\n")
                metrics_names = ['Latency', 'CPU Usage', 'Memory Usage', 
                               'Queue Size', 'Error Rate', 'Throughput']
                for name, value in zip(metrics_names, values):
                    self.metrics_text.insert('end', f"  {name}: {value:.2f}\n")
                self.metrics_text.insert('end', "\n")
                
        except Exception as e:
            print(f"Error updating monitoring: {e}")
            
        finally:
            # Schedule next update
            self.root.after(5000, self._update_monitoring)
            
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
            
            # Log completion
            self.process_text.insert('end', "\n3. Decryption completed successfully\n")
            self.process_text.insert('end', 
                f"   Time taken: {(end_time - start_time).total_seconds():.3f} seconds\n")
            
            # Update statistics
            self.stats_text.delete('1.0', 'end')
            self.stats_text.insert('end', "Decryption Statistics:\n")
            self.stats_text.insert('end', 
                f"Messages processed: {self._message_count}\n")
            self.stats_text.insert('end',
                f"Average processing time: {self._avg_time:.3f} seconds\n")
            
            # Display decrypted message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.message_text.insert('end', 
                f"\n[{timestamp}] Received message:\n{decrypted.decode()}\n")
            self.message_text.see('end')
            
            self.status_var.set("Message received and decrypted successfully")
            
            # Log event
            self.audit_log.log_event(
                AuditEvent(
                    timestamp=datetime.now().timestamp(),
                    event_type="MESSAGE_DECRYPTED",
                    user_id="receiver",
                    action="decrypt_message",
                    status="SUCCESS",
                    details={"message_size": len(decrypted)}
                )
            )
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            self.status_var.set(error_msg)
            self.process_text.insert('end', f"\nError: {error_msg}\n")
            
        finally:
            # Auto-scroll process log
            self.process_text.see('end')
            
    def _start_receiver(self):
        """Start the message receiver"""
        self._message_count = 0
        self._avg_time = 0
        self.receiver.start(self._handle_message)
        self.status_var.set("Listening for messages...")
        
    def _stop_receiver(self):
        """Stop the message receiver"""
        self.receiver.stop()
        self.status_var.set("Receiver stopped")
        
    def _clear_messages(self):
        """Clear the message display"""
        self.message_text.delete('1.0', 'end')
        
    def _clear_logs(self):
        """Clear the audit logs"""
        self.log_text.delete('1.0', 'end')
        
    def _export_logs(self):
        """Export audit logs to file"""
        # Implementation for log export
        pass
        
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

def main():
    gui = ReceiverGUI()
    gui.run()

if __name__ == "__main__":
    main() 