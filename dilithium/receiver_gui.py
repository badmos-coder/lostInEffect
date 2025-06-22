import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from typing import Dict, Tuple
import threading
from datetime import datetime
import os
from dilithium.network.protocol import CryptoNetworkProtocol, MessageReceiver
from dilithium.security.audit import SecureAuditLog, AuditEvent
from dilithium.monitoring.health import HealthCheck
from dilithium.monitoring.metrics import MonitoringSystem
from dilithium.config import SecurityConfig
from dilithium.chaos import HybridEncryption
from dilithium.core import DilithiumParams
import time
import json

class ReceiverGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quantum-Resistant Message Receiver")
        self.root.geometry("1200x800")
        
        # Initialize statistics counters
        self._message_count = 0
        self._file_count = 0
        self._avg_time = 0.0
        self._total_time = 0.0
        
        # Create downloads directory
        self.downloads_dir = os.path.join(os.getcwd(), "received_files")
        if not os.path.exists(self.downloads_dir):
            os.makedirs(self.downloads_dir)
        
        # Initialize components
        self.config = SecurityConfig()
        self.params = DilithiumParams.get_params(security_level=3)
        self.hybrid = HybridEncryption(self.params)
        self.audit_log = SecureAuditLog(self.config)
        self.monitoring = MonitoringSystem(self.config)
        self.health = HealthCheck(self.config, self.monitoring)
        
        # Log initialization
        self.audit_log.log_event(AuditEvent(
            timestamp=datetime.now().timestamp(),
            event_type="SYSTEM_INIT",
            user_id="system",
            action="initialize_receiver",
            status="SUCCESS",
            details={"security_level": 3}
        ))
        
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
        self.files_tab = ttk.Frame(self.notebook)
        self.decryption_tab = ttk.Frame(self.notebook)
        self.monitoring_tab = ttk.Frame(self.notebook)
        self.logs_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.messages_tab, text='Messages')
        self.notebook.add(self.files_tab, text='Files')
        self.notebook.add(self.decryption_tab, text='Decryption Process')
        self.notebook.add(self.monitoring_tab, text='System Monitoring')
        self.notebook.add(self.logs_tab, text='Audit Logs')
        
        self._setup_messages_tab()
        self._setup_files_tab()
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
                  
    def _setup_files_tab(self):
        # Status frame for files
        file_status_frame = ttk.LabelFrame(self.files_tab, text="File Reception Status")
        file_status_frame.pack(fill='x', padx=10, pady=5)
        
        self.file_status_var = tk.StringVar(value="No files received yet...")
        ttk.Label(file_status_frame, 
                 textvariable=self.file_status_var,
                 font=('Helvetica', 10)).pack(padx=5, pady=5)
        
        # Downloads directory info
        dir_frame = ttk.LabelFrame(self.files_tab, text="Download Directory")
        dir_frame.pack(fill='x', padx=10, pady=5)
        
        dir_info_frame = ttk.Frame(dir_frame)
        dir_info_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(dir_info_frame, text="Files saved to:").pack(side='left', padx=5)
        ttk.Label(dir_info_frame, text=self.downloads_dir, 
                 relief='sunken', font=('Courier', 9)).pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(dir_info_frame, text="Open Folder",
                  command=self._open_downloads_folder).pack(side='right', padx=5)
        
        # Received files list
        files_frame = ttk.LabelFrame(self.files_tab, text="Received Files")
        files_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create treeview for file list
        columns = ('Filename', 'Size', 'Type', 'Received', 'Status')
        self.files_tree = ttk.Treeview(files_frame, columns=columns, show='headings', height=15)
        
        # Define column headings and widths
        self.files_tree.heading('Filename', text='Filename')
        self.files_tree.heading('Size', text='Size')
        self.files_tree.heading('Type', text='Type')
        self.files_tree.heading('Received', text='Received')
        self.files_tree.heading('Status', text='Status')
        
        self.files_tree.column('Filename', width=200)
        self.files_tree.column('Size', width=100)
        self.files_tree.column('Type', width=80)
        self.files_tree.column('Received', width=150)
        self.files_tree.column('Status', width=100)
        
        # Add scrollbar
        files_scrollbar = ttk.Scrollbar(files_frame, orient='vertical', command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=files_scrollbar.set)
        
        self.files_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        files_scrollbar.pack(side='right', fill='y', pady=5)
        
        # File action buttons
        file_button_frame = ttk.Frame(self.files_tab)
        file_button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(file_button_frame, text="Clear File List",
                  command=self._clear_file_list).pack(side='left', padx=5)
        ttk.Button(file_button_frame, text="Open Selected",
                  command=self._open_selected_file).pack(side='left', padx=5)
        
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
        """Setup the audit logs tab"""
        # Audit log display
        log_frame = ttk.LabelFrame(self.logs_tab, text="System Audit Logs")
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Add filter frame
        filter_frame = ttk.Frame(log_frame)
        filter_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Filter by:").pack(side='left', padx=5)
        self.filter_var = tk.StringVar(value="ALL")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                  values=["ALL", "SYSTEM_INIT", "RECEIVER_START",
                                         "MESSAGE_RECEIVED", "MESSAGE_DECRYPTED",
                                         "FILE_RECEIVED", "FILE_DECRYPTED",
                                         "RECEIVER_STOP", "RECEIVER_ERROR"])
        filter_combo.pack(side='left', padx=5)
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self._refresh_logs())
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=30, font=('Courier', 10))
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(log_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="Clear Display",
                  command=self._clear_logs).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Export Logs",
                  command=self._export_logs).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Refresh",
                  command=self._refresh_logs).pack(side='left', padx=5)
        
        # Start automatic updates
        self._update_logs()
        
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
            
    def _handle_message(self, data_type, components):
        """Handle received data (message or file) with detailed decryption process"""
        try:
            # Unpack components
            ciphertext = components['ciphertext']
            nonce = components['nonce'] 
            signature = components['signature']
            public_key = components['public_key']
            
            # Log decryption process
            data_description = "file" if data_type == "file" else "message"
            self.process_text.insert('end', 
                f"\n[{datetime.now()}] Starting {data_description} decryption process:\n")
            
            # Log signature verification
            self.process_text.insert('end', "\n1. Verifying signature...\n")
            self.process_text.insert('end', f"   Signature size: {len(signature[0])} bytes\n")
            self.process_text.insert('end', f"   Public key components: {list(public_key.keys())}\n")
            
            # Log decryption
            self.process_text.insert('end', f"\n2. Decrypting {data_description}...\n")
            self.process_text.insert('end', f"   Ciphertext size: {len(ciphertext)} bytes\n")
            self.process_text.insert('end', f"   Nonce size: {len(nonce)} bytes\n")
            
            # Perform decryption
            start_time = time.time()
            decrypted = self.hybrid.verify_and_decrypt(
                ciphertext, nonce, signature, public_key)
            end_time = time.time()
            
            # Update statistics
            process_time = end_time - start_time
            if data_type == "file":
                self._file_count += 1
            else:
                self._message_count += 1
            self._total_time += process_time
            total_items = self._message_count + self._file_count
            self._avg_time = self._total_time / total_items if total_items > 0 else 0
            
            # Log completion
            self.process_text.insert('end', f"\n3. {data_description.capitalize()} decryption completed successfully\n")
            self.process_text.insert('end', 
                f"   Time taken: {process_time:.3f} seconds\n")
            self.process_text.insert('end',
                f"   Original {data_description} size: {len(decrypted)} bytes\n")
            
            # Update statistics display
            self.stats_text.delete('1.0', 'end')
            self.stats_text.insert('end', "Decryption Statistics:\n")
            self.stats_text.insert('end', 
                f"Messages processed: {self._message_count}\n")
            self.stats_text.insert('end', 
                f"Files processed: {self._file_count}\n")
            self.stats_text.insert('end',
                f"Average processing time: {self._avg_time:.3f} seconds\n")
            self.stats_text.insert('end',
                f"Total processing time: {self._total_time:.3f} seconds\n")
            self.stats_text.insert('end',
                f"Last {data_description} size: {len(decrypted)} bytes\n")
            
            if data_type == "file":
                # Handle file data
                filename = components['filename']
                file_size = components['file_size']
                file_type = components.get('file_type', '')
                
                # Save file to downloads directory
                safe_filename = self._get_safe_filename(filename)
                file_path = os.path.join(self.downloads_dir, safe_filename)
                
                with open(file_path, 'wb') as f:
                    f.write(decrypted)
                
                # Add to files tree
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.files_tree.insert('', 'end', values=(
                    safe_filename,
                    f"{file_size:,} bytes",
                    file_type,
                    timestamp,
                    "Received"
                ))
                
                self.file_status_var.set(f"File '{safe_filename}' received and decrypted successfully")
                
                # Display file info in message area
                self.message_text.insert('end', 
                    f"\n[{timestamp}] Received file: {safe_filename}\n")
                self.message_text.insert('end', 
                    f"File size: {file_size:,} bytes\n")
                self.message_text.insert('end', 
                    f"Saved to: {file_path}\n")
                self.message_text.see('end')
                
                # Log file event
                self.audit_log.log_event(
                    AuditEvent(
                        timestamp=datetime.now().timestamp(),
                        event_type="FILE_DECRYPTED",
                        user_id="receiver",
                        action="decrypt_file",
                        status="SUCCESS",
                        details={
                            "filename": safe_filename,
                            "file_size": file_size,
                            "file_type": file_type,
                            "process_time": process_time,
                            "total_files": self._file_count,
                            "saved_path": file_path
                        }
                    )
                )
            else:
                # Display decrypted message
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.message_text.insert('end', 
                    f"\n[{timestamp}] Received message:\n{decrypted.decode()}\n")
                self.message_text.see('end')
                
                self.status_var.set("Message received and decrypted successfully")
                
                # Log message event
                self.audit_log.log_event(
                    AuditEvent(
                        timestamp=datetime.now().timestamp(),
                        event_type="MESSAGE_DECRYPTED",
                        user_id="receiver",
                        action="decrypt_message",
                        status="SUCCESS",
                        details={
                            "message_size": len(decrypted),
                            "process_time": process_time,
                            "total_messages": self._message_count
                        }
                    )
                )
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            self.status_var.set(error_msg)
            self.process_text.insert('end', f"\nError: {error_msg}\n")
            
        finally:
            # Auto-scroll process log
            self.process_text.see('end')
            self.process_text.see('end')
            
    def _start_receiver(self):
        """Start the message receiver"""
        try:
            self._message_count = 0
            self._avg_time = 0
            self.receiver.start(self._handle_message)
            self.status_var.set("Listening for messages...")
            
            # Log receiver start
            self.audit_log.log_event(AuditEvent(
                timestamp=datetime.now().timestamp(),
                event_type="RECEIVER_START",
                user_id="system",
                action="start_listener",
                status="SUCCESS",
                details={"port": self.receiver.port}
            ))
        except Exception as e:
            self.status_var.set(f"Failed to start receiver: {str(e)}")
            self.audit_log.log_event(AuditEvent(
                timestamp=datetime.now().timestamp(),
                event_type="RECEIVER_ERROR",
                user_id="system",
                action="start_listener",
                status="FAILED",
                details={"error": str(e)}
            ))
        
    def _stop_receiver(self):
        """Stop the message receiver"""
        try:
            self.receiver.stop()
            self.status_var.set("Receiver stopped")
            
            # Log receiver stop
            self.audit_log.log_event(AuditEvent(
                timestamp=datetime.now().timestamp(),
                event_type="RECEIVER_STOP",
                user_id="system",
                action="stop_listener",
                status="SUCCESS",
                details={"total_messages": self._message_count}
            ))
        except Exception as e:
            self.status_var.set(f"Error stopping receiver: {str(e)}")
            self.audit_log.log_event(AuditEvent(
                timestamp=datetime.now().timestamp(),
                event_type="RECEIVER_ERROR",
                user_id="system",
                action="stop_listener",
                status="FAILED",
                details={"error": str(e)}
            ))
        
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
        
    def _update_logs(self):
        """Update audit logs display"""
        try:
            logs = self.audit_log.get_logs()
            filter_type = self.filter_var.get()
            
            # Clear current display
            self.log_text.delete('1.0', 'end')
            
            # Display each log entry
            for log in reversed(logs):  # Show newest first
                if filter_type == "ALL" or log.event_type == filter_type:
                    timestamp = datetime.fromtimestamp(log.timestamp)
                    self.log_text.insert('end', 
                        f"\n[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
                        f"{log.event_type}\n")
                    self.log_text.insert('end',
                        f"  User: {log.user_id}\n")
                    self.log_text.insert('end',
                        f"  Action: {log.action}\n")
                    self.log_text.insert('end',
                        f"  Status: {log.status}\n")
                    self.log_text.insert('end',
                        f"  Details: {json.dumps(log.details, indent=2)}\n")
                    self.log_text.insert('end',
                        f"  Hash: {log.hash[:16]}...\n")
                    self.log_text.insert('end', "-" * 80 + "\n")
            
            # Add timestamp of last update
            self.log_text.insert('end', 
                f"\nLast updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
        except Exception as e:
            self.log_text.insert('end', f"\nError updating logs: {str(e)}\n")
        
        finally:
            # Schedule next update
            self.root.after(2000, self._update_logs)

    def _refresh_logs(self):
        """Manually refresh audit logs"""
        self._update_logs()
        
    def _get_safe_filename(self, filename):
        """Generate a safe filename to avoid overwriting existing files"""
        safe_name = os.path.basename(filename)  # Remove any path components
        
        # Remove or replace potentially dangerous characters
        import re
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', safe_name)
        
        # If file already exists, add a number suffix
        base_path = os.path.join(self.downloads_dir, safe_name)
        if os.path.exists(base_path):
            name, ext = os.path.splitext(safe_name)
            counter = 1
            while os.path.exists(os.path.join(self.downloads_dir, f"{name}_{counter}{ext}")):
                counter += 1
            safe_name = f"{name}_{counter}{ext}"
        
        return safe_name
        
    def _open_downloads_folder(self):
        """Open the downloads folder in the system file manager"""
        try:
            import subprocess
            import sys
            
            if sys.platform == "win32":
                os.startfile(self.downloads_dir)
            elif sys.platform == "darwin":
                subprocess.run(["open", self.downloads_dir])
            else:
                subprocess.run(["xdg-open", self.downloads_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open downloads folder: {str(e)}")
            
    def _clear_file_list(self):
        """Clear the received files list"""
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        self.file_status_var.set("File list cleared")
        
    def _open_selected_file(self):
        """Open the selected file in the default system application"""
        try:
            selected = self.files_tree.selection()
            if not selected:
                messagebox.showinfo("No Selection", "Please select a file to open.")
                return
                
            item = self.files_tree.item(selected[0])
            filename = item['values'][0]
            file_path = os.path.join(self.downloads_dir, filename)
            
            if not os.path.exists(file_path):
                messagebox.showerror("File Not Found", f"File {filename} not found in downloads folder.")
                return
                
            import subprocess
            import sys
            
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", file_path])
            else:
                subprocess.run(["xdg-open", file_path])
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")
        
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

def main():
    gui = ReceiverGUI()
    gui.run()

if __name__ == "__main__":
    main() 