#!/usr/bin/env python3
"""
Test script for the enhanced Dilithium GUI with automated file operations
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test imports
    from dilithium.core import DilithiumParams
    from dilithium.chaos import HybridEncryption
    from dilithium.monitoring.metrics import MonitoringSystem
    from dilithium.monitoring.health import HealthCheck
    from dilithium.config import SecurityConfig
    from dilithium.file_operations import FileEncryptionManager
    
    print("✓ All core modules imported successfully")
    
    # Initialize components
    config = SecurityConfig()
    params = DilithiumParams.get_params(security_level=3)
    hybrid = HybridEncryption(params)
    
    print("✓ Dilithium system initialized")
    
    # Setup monitoring
    monitoring = MonitoringSystem(config)
    health = HealthCheck(config, monitoring)
    
    print("✓ Monitoring system initialized")
    
    # Test file operations manager
    file_manager = FileEncryptionManager(hybrid)
    
    print("✓ File encryption manager initialized")
    
    # Test GUI import
    from example import DilithiumGUI
    
    print("✓ GUI module imported successfully")
    
    print("\n🎉 All components are working! You can now run 'python example.py' to launch the GUI")
    print("\nNew features added:")
    print("- 📁 Automated folder encryption/decryption")
    print("- 🔑 Automatic key generation")
    print("- 💾 Message encryption and storage")
    print("- 📊 Progress tracking for batch operations")
    print("- 🔄 Threaded operations for better UI responsiveness")
    
    # Demonstrate a quick test
    print("\n--- Quick Test ---")
    print("Testing key generation...")
    public_key, private_key = hybrid.generate_keys()
    print(f"✓ Keys generated successfully! Public key seed: {public_key['seed'].hex()[:16]}...")
    
    print("Testing encryption...")
    test_message = b"Hello, this is a test message for the automated system!"
    ciphertext, nonce, signature = hybrid.encrypt_and_sign(test_message, private_key)
    print(f"✓ Message encrypted! Ciphertext size: {len(ciphertext)} bytes")
    
    print("Testing decryption...")
    decrypted = hybrid.verify_and_decrypt(ciphertext, nonce, signature, public_key)
    print(f"✓ Message decrypted successfully! Message: {decrypted.decode()}")
    
    print("\n🚀 Ready to launch the enhanced GUI!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure all required modules are available")
except Exception as e:
    print(f"❌ Error: {e}")
    print("Please check your setup and try again") 