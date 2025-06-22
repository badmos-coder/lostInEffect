import socket
import json
import threading
import numpy as np
from typing import Dict, Any, Optional, Tuple
from ..security.audit import SecureAuditLog, AuditEvent
from datetime import datetime
import struct
import base64
import os

class CryptoNetworkProtocol:
    """Protocol for secure message transmission"""
    
    def __init__(self, audit_log: SecureAuditLog):
        self.audit_log = audit_log
        
    def pack_message(self, ciphertext: bytes, nonce: bytes, 
                    signature: Tuple[bytes, np.ndarray], public_key: Dict) -> bytes:
        """Pack encrypted message and metadata for transmission"""
        # Convert signature components
        mu, z = signature
        z_bytes = z.tobytes()
        
        # Convert public key components
        key_data = {
            'seed': base64.b64encode(public_key['seed']).decode(),
            't': [arr.tolist() for arr in public_key['t']]
        }
        
        # Create message dictionary
        message_dict = {
            'type': 'message',
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'nonce': base64.b64encode(nonce).decode(),
            'mu': base64.b64encode(mu).decode(),
            'z': base64.b64encode(z_bytes).decode(),
            'public_key': key_data
        }
        
        # Convert to JSON and encode
        return json.dumps(message_dict).encode()
        
    def pack_file(self, ciphertext: bytes, nonce: bytes, 
                  signature: Tuple[bytes, np.ndarray], public_key: Dict,
                  filename: str, file_size: int, file_type: str = None) -> bytes:
        """Pack encrypted file data and metadata for transmission"""
        # Convert signature components
        mu, z = signature
        z_bytes = z.tobytes()
        
        # Convert public key components
        key_data = {
            'seed': base64.b64encode(public_key['seed']).decode(),
            't': [arr.tolist() for arr in public_key['t']]
        }
        
        # Create file dictionary
        file_dict = {
            'type': 'file',
            'filename': filename,
            'file_size': file_size,
            'file_type': file_type or os.path.splitext(filename)[1],
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'nonce': base64.b64encode(nonce).decode(),
            'mu': base64.b64encode(mu).decode(),
            'z': base64.b64encode(z_bytes).decode(),
            'public_key': key_data
        }
        
        # Convert to JSON and encode
        return json.dumps(file_dict).encode()
        
    def unpack_message(self, data: bytes) -> Tuple[bytes, bytes, Tuple[bytes, np.ndarray], Dict]:
        """Unpack received message into components"""
        try:
            # Parse JSON message
            message_dict = json.loads(data.decode())
            
            # Extract and decode components
            ciphertext = base64.b64decode(message_dict['ciphertext'])
            nonce = base64.b64decode(message_dict['nonce'])
            mu = base64.b64decode(message_dict['mu'])
            z_bytes = base64.b64decode(message_dict['z'])
            
            # Reconstruct z array
            z = np.frombuffer(z_bytes, dtype=np.int32)
            
            # Reconstruct public key
            public_key = {
                'seed': base64.b64decode(message_dict['public_key']['seed']),
                't': [np.array(t, dtype=np.int32) for t in message_dict['public_key']['t']]
            }
            
            return ciphertext, nonce, (mu, z), public_key
            
        except Exception as e:
            raise ValueError(f"Failed to unpack message: {str(e)}")
            
    def unpack_data(self, data: bytes) -> Tuple[str, Dict]:
        """Unpack received data and return type and components"""
        try:
            # Parse JSON data
            data_dict = json.loads(data.decode())
            data_type = data_dict.get('type', 'message')
            
            # Extract and decode components
            ciphertext = base64.b64decode(data_dict['ciphertext'])
            nonce = base64.b64decode(data_dict['nonce'])
            mu = base64.b64decode(data_dict['mu'])
            z_bytes = base64.b64decode(data_dict['z'])
            
            # Reconstruct z array
            z = np.frombuffer(z_bytes, dtype=np.int32)
            
            # Reconstruct public key
            public_key = {
                'seed': base64.b64decode(data_dict['public_key']['seed']),
                't': [np.array(t, dtype=np.int32) for t in data_dict['public_key']['t']]
            }
            
            components = {
                'ciphertext': ciphertext,
                'nonce': nonce,
                'signature': (mu, z),
                'public_key': public_key
            }
            
            # Add file-specific metadata if it's a file
            if data_type == 'file':
                components.update({
                    'filename': data_dict['filename'],
                    'file_size': data_dict['file_size'],
                    'file_type': data_dict.get('file_type', '')
                })
            
            return data_type, components
            
        except Exception as e:
            raise ValueError(f"Failed to unpack data: {str(e)}")

class MessageSender:
    """Handles sending encrypted messages"""
    
    def __init__(self, protocol: CryptoNetworkProtocol, 
                 host: str = 'localhost', port: int = 5000):
        self.protocol = protocol
        self.host = host
        self.port = port
        
    def send_message(self, message_data: bytes) -> None:
        """Send packed message over network"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host, self.port))
                
                # Send message size first
                size = len(message_data)
                sock.sendall(struct.pack('>I', size))
                
                # Send message data
                sock.sendall(message_data)
                
                # Wait for acknowledgment
                ack = sock.recv(2)
                if ack != b'OK':
                    raise RuntimeError("Failed to receive acknowledgment")
                
                # Log success
                self.protocol.audit_log.log_event(
                    AuditEvent(
                        timestamp=datetime.now().timestamp(),
                        event_type="MESSAGE_SENT",
                        user_id="sender",
                        action="send_message",
                        status="SUCCESS",
                        details={"host": self.host, "port": self.port}
                    )
                )
        except Exception as e:
            raise RuntimeError(f"Failed to send message: {str(e)}")

class MessageReceiver:
    """Handles receiving encrypted messages"""
    
    def __init__(self, protocol: CryptoNetworkProtocol,
                 port: int = 5000):
        self.protocol = protocol
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', port))
        self.running = False
        self.callback = None
        
    def start(self, callback) -> None:
        """Start listening for messages"""
        self.callback = callback
        self.running = True
        self.socket.listen(1)
        
        # Start listener thread
        thread = threading.Thread(target=self._listen)
        thread.daemon = True
        thread.start()
        
    def stop(self) -> None:
        """Stop listening for messages"""
        self.running = False
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        self.socket.close()
        
    def _listen(self) -> None:
        """Listen for incoming messages"""
        while self.running:
            try:
                conn, addr = self.socket.accept()
                with conn:
                    # Receive message size first
                    size_data = conn.recv(4)
                    if not size_data:
                        continue
                    
                    size = struct.unpack('>I', size_data)[0]
                    
                    # Receive message data
                    data = b''
                    while len(data) < size:
                        chunk = conn.recv(min(size - len(data), 4096))
                        if not chunk:
                            break
                        data += chunk
                    
                    if len(data) == size:
                        # Send acknowledgment
                        conn.sendall(b'OK')
                        
                        # Process data (message or file)
                        if self.callback:
                            try:
                                data_type, components = self.protocol.unpack_data(data)
                                self.callback(data_type, components)
                                
                                # Log success
                                event_type = "FILE_RECEIVED" if data_type == "file" else "MESSAGE_RECEIVED"
                                self.protocol.audit_log.log_event(
                                    AuditEvent(
                                        timestamp=datetime.now().timestamp(),
                                        event_type=event_type,
                                        user_id="receiver",
                                        action=f"receive_{data_type}",
                                        status="SUCCESS",
                                        details={"from": addr[0], "type": data_type}
                                    )
                                )
                            except Exception as e:
                                print(f"Error processing {data_type}: {e}")
                    
            except Exception as e:
                if self.running:
                    print(f"Error receiving message: {e}") 