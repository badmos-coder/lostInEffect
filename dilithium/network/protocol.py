import socket
import json
import threading
import numpy as np
from typing import Dict, Any, Optional, Tuple
from ..security.audit import SecureAuditLog, AuditEvent
from datetime import datetime
import struct
import base64

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
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'nonce': base64.b64encode(nonce).decode(),
            'mu': base64.b64encode(mu).decode(),
            'z': base64.b64encode(z_bytes).decode(),
            'public_key': key_data
        }
        
        # Convert to JSON and encode
        return json.dumps(message_dict).encode()
        
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
                        
                        # Process message
                        if self.callback:
                            try:
                                message_components = self.protocol.unpack_message(data)
                                self.callback(message_components)
                                
                                # Log success
                                self.protocol.audit_log.log_event(
                                    AuditEvent(
                                        timestamp=datetime.now().timestamp(),
                                        event_type="MESSAGE_RECEIVED",
                                        user_id="receiver",
                                        action="receive_message",
                                        status="SUCCESS",
                                        details={"from": addr[0]}
                                    )
                                )
                            except Exception as e:
                                print(f"Error processing message: {e}")
                    
            except Exception as e:
                if self.running:
                    print(f"Error receiving message: {e}") 