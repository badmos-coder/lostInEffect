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
from dilithium.gui import DilithiumGUI

def print_key(name: str, key: dict):
    print(f"\n{name}:")
    for k, v in key.items():
        if isinstance(v, np.ndarray):
            print(f"  {k}: array of shape {v.shape}, first few values: {v.flatten()[:5]}")
        else:
            print(f"  {k}: {v[:20]}..." if isinstance(v, bytes) else f"  {k}: {v}")

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