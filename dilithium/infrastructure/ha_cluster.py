from typing import List, Dict, Optional
import redis
from redis.sentinel import Sentinel
import threading
import time
import hashlib
import secrets
from dilithium.config import SecurityConfig
from ..security.key_management import KeyManager

class HACluster:
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.node_id = hashlib.sha256(secrets.token_bytes(32)).hexdigest()[:8]
        self.sentinel = self._setup_sentinel()
        self.key_manager = KeyManager(config)
        self.lock = threading.Lock()
        self._is_master = False
        
    def _setup_sentinel(self) -> Sentinel:
        """Setup Redis Sentinel for HA"""
        sentinel_hosts = [
            ('sentinel1', 26379),
            ('sentinel2', 26379),
            ('sentinel3', 26379)
        ]
        return Sentinel(sentinel_hosts, socket_timeout=0.1)
        
    def _elect_master(self) -> bool:
        """Leader election process"""
        with self.lock:
            master = self.sentinel.discover_master('dilithium-cluster')
            if not master:
                # No master exists, attempt to become master
                if self.sentinel.master_for('dilithium-cluster', socket_timeout=0.1):
                    self._is_master = True
                    return True
            return False
            
    def replicate_state(self, state: Dict) -> None:
        """Replicate state to all nodes"""
        if self._is_master:
            master = self.sentinel.master_for('dilithium-cluster')
            master.set('cluster_state', str(state))
            
    def process_request(self, request: Dict) -> Dict:
        """Process request with HA guarantees"""
        if not self._is_master:
            # Forward to master if this is a slave
            master = self.sentinel.master_for('dilithium-cluster')
            return self._forward_request(master, request)
            
        # Process on master
        result = self._handle_request(request)
        self.replicate_state({'last_request': request, 'result': result})
        return result 