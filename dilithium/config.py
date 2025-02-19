from dataclasses import dataclass
from typing import Dict, Optional
import yaml
import os
from cryptography.fernet import Fernet

@dataclass
class SecurityConfig:
    key_rotation_interval: int = 3600  # 1 hour
    min_key_length: int = 256
    max_sessions: int = 1000
    audit_level: str = "HIGH"
    fips_mode: bool = True
    hsm_enabled: bool = True
    
    def __init__(self, hsm_enabled: bool = False):
        self.hsm_enabled = hsm_enabled
        self.key_rotation_days = 90
        self.min_key_length = 256

@dataclass
class SystemConfig:
    max_threads: int = 8
    batch_size: int = 100
    cache_size: int = 1024
    timeout: int = 30
    retry_attempts: int = 3

class SecureConfiguration:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self._load_config()
        
    def _load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                self.security = SecurityConfig(**config_data.get('security', {}))
                self.system = SystemConfig(**config_data.get('system', {}))
        except FileNotFoundError:
            # Use default configurations
            self.security = SecurityConfig()
            self.system = SystemConfig() 