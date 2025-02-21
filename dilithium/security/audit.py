from dilithium.config import SecurityConfig
import logging
from datetime import datetime
import json
from typing import Dict, Any, List
import hashlib
from dataclasses import dataclass
from collections import deque

@dataclass
class AuditEvent:
    timestamp: float
    event_type: str
    user_id: str
    action: str
    status: str
    details: Dict[str, Any]
    hash: str = ""

class SecureAuditLog:
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.previous_hash = None
        self.logs = deque(maxlen=1000)  # Store last 1000 logs
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def log_event(self, event: AuditEvent) -> None:
        """Log a secure, tamper-evident audit event"""
        try:
            # Create event data dictionary
            event_data = {
                'timestamp': event.timestamp,
                'type': event.event_type,
                'user': event.user_id,
                'action': event.action,
                'status': event.status,
                'details': event.details
            }
            
            # Create tamper-evident chain
            data_string = json.dumps(event_data, sort_keys=True)
            prev_hash = self.previous_hash or ''
            event.hash = hashlib.sha3_256(
                f"{prev_hash}{data_string}".encode()
            ).hexdigest()
            
            # Store log
            self.logs.append(event)
            self.previous_hash = event.hash
            
            # Log to file
            logging.info(json.dumps({**event_data, 'hash': event.hash}))
            
        except Exception as e:
            logging.error(f"Failed to log event: {str(e)}")
            
    def get_logs(self) -> List[AuditEvent]:
        """Retrieve all stored logs"""
        return list(self.logs)
        
    def verify_chain(self) -> bool:
        """Verify the integrity of the log chain"""
        try:
            prev_hash = None
            for event in self.logs:
                # Recreate event data
                event_data = {
                    'timestamp': event.timestamp,
                    'type': event.event_type,
                    'user': event.user_id,
                    'action': event.action,
                    'status': event.status,
                    'details': event.details
                }
                
                # Verify hash
                data_string = json.dumps(event_data, sort_keys=True)
                computed_hash = hashlib.sha3_256(
                    f"{prev_hash or ''}{data_string}".encode()
                ).hexdigest()
                
                if computed_hash != event.hash:
                    return False
                    
                prev_hash = event.hash
                
            return True
            
        except Exception as e:
            logging.error(f"Failed to verify log chain: {str(e)}")
            return False 