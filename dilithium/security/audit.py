from dilithium.config import SecurityConfig
import logging
from datetime import datetime
import json
from typing import Dict, Any
import hashlib
from dataclasses import dataclass

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
        self._setup_logging()
        self.previous_hash = None
        
    def _setup_logging(self):
        """Configure secure logging"""
        logging.basicConfig(
            filename='secure_audit.log',
            level=logging.INFO,
            format='%(asctime)s|%(message)s|%(hash)s'
        )
        
    def log_event(self, event: AuditEvent) -> None:
        """Log a secure, tamper-evident audit event"""
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
        
        # Log with hash
        logging.info(json.dumps({**event_data, 'hash': event.hash}))
        self.previous_hash = event.hash 