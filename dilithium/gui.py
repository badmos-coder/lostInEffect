import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import time
from typing import Dict, Any
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from .monitoring.metrics import MonitoringSystem, PerformanceMetrics
from .monitoring.health import HealthCheck
from .security.audit import SecureAuditLog, AuditEvent
import psutil
import os

class DilithiumGUI:
    def __init__(self, hybrid_system, monitoring: MonitoringSystem, health: HealthCheck):
        self.root = tk.Tk()
        self.root.title("Quantum-Resistant Encryption System")
        self.root.geometry("1600x1000")  # Increased window size
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('Title.TLabel', font=('Helvetica', 14, 'bold'))
        self.style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        self.style.configure('Status.TLabel', font=('Helvetica', 11))
        self.style.configure('Custom.TButton', font=('Helvetica', 10))
        
        # Configure colors
        self.root.configure(bg='#f0f0f0')
        self.style.configure('Custom.TFrame', background='#f0f0f0')
        
        self.hybrid = hybrid_system
        self.monitoring = monitoring
        self.health = health
        self.log_queue = queue.Queue()
        
        # Initialize data storage for graphs
        self.time_points = []
        self.cpu_points = []
        self.memory_points = []
        self.latency_points = []
        
        # Get the current process for monitoring
        self.process = psutil.Process(os.getpid())
        
        self._setup_gui()
        self._start_monitoring()
        
    def _setup_gui(self):
        # Main title
        title_frame = ttk.Frame(self.root, style='Custom.TFrame')
        title_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(title_frame, text="Quantum-Resistant Cryptography System", 
                 style='Title.TLabel').pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Manual Mode Tab (existing encryption tab with new name)
        manual_frame = ttk.Frame(notebook, style='Custom.TFrame')
        notebook.add(manual_frame, text='Manual Mode')
        self._setup_encryption_tab(manual_frame)
        
        # Automatic Mode Tab
        auto_frame = ttk.Frame(notebook, style='Custom.TFrame')
        notebook.add(auto_frame, text='Automatic Mode')
        self._setup_automatic_tab(auto_frame)
        
        # Monitoring Tab
        monitor_frame = ttk.Frame(notebook, style='Custom.TFrame')
        notebook.add(monitor_frame, text='System Monitoring')
        self._setup_monitoring_tab(monitor_frame)
        
        # Audit Log Tab
        audit_frame = ttk.Frame(notebook, style='Custom.TFrame')
        notebook.add(audit_frame, text='Audit Log')
        self._setup_audit_tab(audit_frame)
        
        # Health Status Tab
        health_frame = ttk.Frame(notebook, style='Custom.TFrame')
        notebook.add(health_frame, text='Health Status')
        self._setup_health_tab(health_frame)
        
    def _setup_encryption_tab(self, parent):
        # Input frame
        input_frame = ttk.LabelFrame(parent, text="Message Input", padding=15)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(input_frame, text="Enter Message:", style='Header.TLabel').pack(side='left', padx=5)
        self.message_entry = ttk.Entry(input_frame, width=80, font=('Helvetica', 10))
        self.message_entry.pack(side='left', padx=10)
        
        # Buttons frame
        button_frame = ttk.Frame(parent, style='Custom.TFrame')
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Generate Keys", style='Custom.TButton',
                  command=self._generate_keys).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Encrypt & Sign", style='Custom.TButton',
                  command=self._encrypt_sign).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Verify & Decrypt", style='Custom.TButton',
                  command=self._verify_decrypt).pack(side='left', padx=5)
        
        # Output frame
        output_frame = ttk.LabelFrame(parent, text="Encryption Results", padding=15)
        output_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=25, 
                                                    font=('Courier', 10))
        self.output_text.pack(fill='both', expand=True, padx=5, pady=5)
        
    def _setup_automatic_tab(self, parent):
        # Input frame
        input_frame = ttk.LabelFrame(parent, text="Message Input", padding=15)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(input_frame, text="Enter Message:", 
                 style='Header.TLabel').pack(side='left', padx=5)
        self.auto_message_entry = ttk.Entry(input_frame, width=80, 
                                          font=('Helvetica', 10))
        self.auto_message_entry.pack(side='left', padx=10)
        
        # Button frame
        button_frame = ttk.Frame(parent, style='Custom.TFrame')
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Start Automatic Process", 
                  style='Custom.TButton',
                  command=self._run_automatic_process).pack(side='left', padx=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(parent, text="Process Status", padding=15)
        progress_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(progress_frame, 
                                    textvariable=self.status_var,
                                    style='Status.TLabel')
        self.status_label.pack(side='left', padx=5)
        
        self.progress = ttk.Progressbar(progress_frame, length=400, 
                                      mode='determinate')
        self.progress.pack(side='right', padx=5)
        
        # Output frame
        output_frame = ttk.LabelFrame(parent, text="Process Output", padding=15)
        output_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.auto_output_text = scrolledtext.ScrolledText(output_frame, 
                                                         height=25,
                                                         font=('Courier', 10))
        self.auto_output_text.pack(fill='both', expand=True, padx=5, pady=5)

    def _setup_monitoring_tab(self, parent):
        # Metrics frame with real-time updates
        metrics_frame = ttk.LabelFrame(parent, text="Real-time System Metrics", padding=15)
        metrics_frame.pack(fill='x', padx=10, pady=5)
        
        # Create styled labels for metrics
        self.cpu_label = ttk.Label(metrics_frame, text="CPU Usage: 0%", 
                                  style='Status.TLabel')
        self.cpu_label.pack(side='left', padx=20)
        
        self.memory_label = ttk.Label(metrics_frame, text="Memory Usage: 0%", 
                                     style='Status.TLabel')
        self.memory_label.pack(side='left', padx=20)
        
        self.latency_label = ttk.Label(metrics_frame, text="Latency: 0ms", 
                                      style='Status.TLabel')
        self.latency_label.pack(side='left', padx=20)
        
        # Graphs frame
        graphs_frame = ttk.LabelFrame(parent, text="Performance Graphs", padding=15)
        graphs_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        plt.style.use('ggplot')
        
        # Create figure for plotting and store canvas reference
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graphs_frame)  # Store canvas reference
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
    def _setup_audit_tab(self, parent):
        # Header frame
        header_frame = ttk.Frame(parent, style='Custom.TFrame')
        header_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(header_frame, text="System Audit Log", 
                 style='Header.TLabel').pack(side='left', pady=5)
        ttk.Button(header_frame, text="Refresh Logs", style='Custom.TButton',
                  command=self._refresh_audit_logs).pack(side='right', padx=5)
        
        # Log display
        self.audit_text = scrolledtext.ScrolledText(parent, height=35, 
                                                   font=('Courier', 10))
        self.audit_text.pack(fill='both', expand=True, padx=10, pady=5)
        
    def _setup_health_tab(self, parent):
        # Header frame
        header_frame = ttk.Frame(parent, style='Custom.TFrame')
        header_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(header_frame, text="System Health Status", 
                 style='Header.TLabel').pack(side='left', pady=5)
        ttk.Button(header_frame, text="Refresh Status", style='Custom.TButton',
                  command=self._refresh_health_status).pack(side='right', padx=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(parent, text="Current Status", padding=15)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Status: Checking...", 
                                     style='Header.TLabel')
        self.status_label.pack(side='left', padx=5)
        
        # Health details
        self.health_text = scrolledtext.ScrolledText(parent, height=30, 
                                                    font=('Courier', 10))
        self.health_text.pack(fill='both', expand=True, padx=10, pady=5)
        
    def _add_audit_log(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.audit_text.insert('end', f"[{timestamp}] {message}\n")
        self.audit_text.see('end')
        
    def _refresh_audit_logs(self):
        self._add_audit_log("Audit log refreshed")
        self._add_audit_log(f"CPU Usage: {psutil.cpu_percent()}%")
        self._add_audit_log(f"Memory Usage: {psutil.virtual_memory().percent}%")
        
    def _refresh_health_status(self):
        try:
            # Get process-specific metrics
            cpu_percent = self.process.cpu_percent() / psutil.cpu_count()
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            memory_percent = (memory_info.rss / psutil.virtual_memory().total) * 100
            
            health_report = {
                'status': 'HEALTHY',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'program_metrics': {
                    'cpu_usage': f"{cpu_percent:.1f}%",
                    'memory_usage': f"{memory_mb:.1f}MB ({memory_percent:.1f}%)",
                    'threads': len(self.process.threads()),
                    'open_files': len(self.process.open_files()),
                    'encryption_latency': f"{self.health._measure_latency():.2f}ms"
                },
                'encryption_status': {
                    'operations_completed': len(self.time_points),
                    'average_latency': f"{np.mean(self.latency_points):.2f}ms",
                    'max_latency': f"{np.max(self.latency_points):.2f}ms"
                }
            }
            
            # Update status label
            self.status_label.config(
                text=f"Status: {health_report['status']}", 
                foreground='green' if health_report['status'] == 'HEALTHY' else 'red'
            )
            
            # Update health text
            self.health_text.delete('1.0', 'end')
            self.health_text.insert('end', json.dumps(health_report, indent=2))
            
        except Exception as e:
            self.health_text.delete('1.0', 'end')
            self.health_text.insert('end', f"Error refreshing health status: {str(e)}")
        
    def _generate_keys(self):
        try:
            self.public_key, self.private_key = self.hybrid.generate_keys()
            self._add_audit_log("New key pair generated successfully")
            self.output_text.insert('end', "Keys generated successfully!\n")
            self.output_text.insert('end', f"Public Key (seed): {self.public_key['seed'].hex()[:20]}...\n")
            self.output_text.see('end')
        except Exception as e:
            self._add_audit_log(f"Key generation failed: {str(e)}")
            self.output_text.insert('end', f"Error generating keys: {str(e)}\n")
            
    def _encrypt_sign(self):
        try:
            message = self.message_entry.get().encode()
            ciphertext, nonce, signature = self.hybrid.encrypt_and_sign(
                message, self.private_key
            )
            self.ciphertext = ciphertext
            self.nonce = nonce
            self.signature = signature
            
            # Clear previous output
            self.output_text.delete('1.0', 'end')
            
            # Display detailed encryption information
            self.output_text.insert('end', "=== Encryption Results ===\n\n")
            self.output_text.insert('end', f"Original Message: {message.decode()}\n")
            self.output_text.insert('end', f"Message Length: {len(message)} bytes\n\n")
            
            self.output_text.insert('end', "Ciphertext (hex):\n")
            self.output_text.insert('end', f"{ciphertext.hex()}\n\n")
            
            self.output_text.insert('end', "Nonce (hex):\n")
            self.output_text.insert('end', f"{nonce.hex()}\n\n")
            
            self.output_text.insert('end', "Signature:\n")
            mu, z = signature
            self.output_text.insert('end', f"- mu (hex): {mu.hex()}\n")
            self.output_text.insert('end', f"- z shape: {z.shape}, first values: {z.flatten()[:5]}\n\n")
            
            # Add to audit log with detailed information
            self._add_audit_log("=== New Encryption Operation ===")
            self._add_audit_log(f"Original Message: {message.decode()}")
            self._add_audit_log(f"Ciphertext (hex): {ciphertext.hex()[:50]}...")
            self._add_audit_log(f"Nonce (hex): {nonce.hex()}")
            self._add_audit_log(f"Signature mu (hex): {mu.hex()[:50]}...")
            self._add_audit_log("Encryption completed successfully")
            
            self.output_text.see('end')
            
        except Exception as e:
            self._add_audit_log(f"Encryption failed: {str(e)}")
            self.output_text.insert('end', f"Error encrypting: {str(e)}\n")
            
    def _verify_decrypt(self):
        try:
            decrypted = self.hybrid.verify_and_decrypt(
                self.ciphertext, self.nonce, self.signature, self.public_key
            )
            
            # Clear previous output
            self.output_text.delete('1.0', 'end')
            
            # Display detailed decryption information
            self.output_text.insert('end', "=== Decryption Results ===\n\n")
            self.output_text.insert('end', "Verification: Successful\n\n")
            self.output_text.insert('end', f"Decrypted Message: {decrypted.decode()}\n")
            self.output_text.insert('end', f"Message Length: {len(decrypted)} bytes\n")
            
            # Add to audit log
            self._add_audit_log("=== New Decryption Operation ===")
            self._add_audit_log("Signature verification: Successful")
            self._add_audit_log(f"Decrypted Message: {decrypted.decode()}")
            self._add_audit_log("Decryption completed successfully")
            
            self.output_text.see('end')
            
        except Exception as e:
            self._add_audit_log(f"Decryption failed: {str(e)}")
            self.output_text.insert('end', f"Error decrypting: {str(e)}\n")
            
    def _update_graphs(self):
        # Clear previous plots
        self.ax.clear()
        
        # Plot CPU and Memory usage
        self.ax.plot(self.time_points[-50:], self.cpu_points[-50:], 'b-', label='CPU')
        self.ax.plot(self.time_points[-50:], self.memory_points[-50:], 'r-', label='Memory')
        self.ax.set_ylabel('Usage %')
        self.ax.legend()
        self.ax.grid(True)
        
        self.canvas.draw()
        
    def _start_monitoring(self):
        def update_loop():
            while True:
                try:
                    # Get metrics for current process only
                    current_time = time.time()
                    
                    # CPU usage for this process (percent of one CPU)
                    cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
                    
                    # Memory usage for this process (in MB)
                    memory_usage = self.process.memory_info().rss / (1024 * 1024)
                    memory_percent = (memory_usage / psutil.virtual_memory().total) * 100
                    
                    # Measure latency of encryption operations
                    latency = self.health._measure_latency()
                    
                    # Update metrics labels
                    self.cpu_label.config(
                        text=f"Program CPU Usage: {cpu_usage:.1f}%"
                    )
                    self.memory_label.config(
                        text=f"Program Memory Usage: {memory_usage:.1f}MB ({memory_percent:.1f}%)"
                    )
                    self.latency_label.config(
                        text=f"Encryption Latency: {latency:.1f}ms"
                    )
                    
                    # Update graph data
                    self.time_points.append(current_time)
                    self.cpu_points.append(cpu_usage)
                    self.memory_points.append(memory_percent)
                    self.latency_points.append(latency)
                    
                    # Keep only last 50 points
                    if len(self.time_points) > 50:
                        self.time_points = self.time_points[-50:]
                        self.cpu_points = self.cpu_points[-50:]
                        self.memory_points = self.memory_points[-50:]
                        self.latency_points = self.latency_points[-50:]
                    
                    # Update graphs
                    self._update_graphs()
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(1)
                
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
        
    def _run_automatic_process(self):
        def process():
            try:
                message = self.auto_message_entry.get().encode()
                
                # Reset progress and output
                self.progress['value'] = 0
                self.auto_output_text.delete('1.0', 'end')
                
                # Step 1: Generate Keys (25%)
                self.status_var.set("Generating Keys...")
                self.auto_output_text.insert('end', "=== Generating Keys ===\n\n")
                self.public_key, self.private_key = self.hybrid.generate_keys()
                self.auto_output_text.insert('end', 
                    f"Public Key (seed): {self.public_key['seed'].hex()[:20]}...\n")
                self.auto_output_text.insert('end', 
                    f"Private Key (seed): {self.private_key['seed'].hex()[:20]}...\n\n")
                self.progress['value'] = 25
                self.auto_output_text.see('end')
                time.sleep(0.5)  # Allow UI to update
                
                # Step 2: Encryption & Signing (50%)
                self.status_var.set("Encrypting and Signing...")
                self.auto_output_text.insert('end', "=== Encrypting & Signing ===\n\n")
                self.auto_output_text.insert('end', f"Original Message: {message.decode()}\n")
                ciphertext, nonce, signature = self.hybrid.encrypt_and_sign(
                    message, self.private_key
                )
                self.ciphertext = ciphertext
                self.nonce = nonce
                self.signature = signature
                
                self.auto_output_text.insert('end', f"\nCiphertext (hex):\n{ciphertext.hex()}\n")
                self.auto_output_text.insert('end', f"\nNonce (hex):\n{nonce.hex()}\n")
                mu, z = signature
                self.auto_output_text.insert('end', f"\nSignature:\n")
                self.auto_output_text.insert('end', f"- mu (hex): {mu.hex()}\n")
                self.auto_output_text.insert('end', 
                    f"- z shape: {z.shape}, first values: {z.flatten()[:5]}\n\n")
                self.progress['value'] = 50
                self.auto_output_text.see('end')
                time.sleep(0.5)
                
                # Step 3: Verification & Decryption (75%)
                self.status_var.set("Verifying and Decrypting...")
                self.auto_output_text.insert('end', "=== Verifying & Decrypting ===\n\n")
                decrypted = self.hybrid.verify_and_decrypt(
                    ciphertext, nonce, signature, self.public_key
                )
                self.progress['value'] = 75
                time.sleep(0.5)
                
                # Step 4: Final Results (100%)
                self.status_var.set("Process Complete")
                self.auto_output_text.insert('end', "=== Final Results ===\n\n")
                self.auto_output_text.insert('end', "Verification: Successful\n")
                self.auto_output_text.insert('end', f"Decrypted Message: {decrypted.decode()}\n")
                self.auto_output_text.insert('end', 
                    f"Message Integrity: {message == decrypted}\n\n")
                self.progress['value'] = 100
                self.auto_output_text.see('end')
                
                # Add to audit log
                self._add_audit_log("=== Automatic Process Completed ===")
                self._add_audit_log(f"Original Message: {message.decode()}")
                self._add_audit_log(f"Process Status: Success")
                
            except Exception as e:
                self.status_var.set("Error")
                self.auto_output_text.insert('end', f"\nError: {str(e)}\n")
                self._add_audit_log(f"Automatic Process Error: {str(e)}")
        
        # Run in separate thread to keep UI responsive
        threading.Thread(target=process, daemon=True).start()
        
    def run(self):
        # Initial refresh of health and audit
        self._refresh_health_status()
        self._refresh_audit_logs()
        self.root.mainloop() 