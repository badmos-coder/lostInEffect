from dilithium.core import DilithiumParams
from dilithium.keygen import KeyGenerator
from dilithium.sign import Signer
from dilithium.verify import Verifier
import time
import numpy as np

def print_key(name: str, key: dict):
    print(f"\n{name}:")
    for k, v in key.items():
        if isinstance(v, np.ndarray):
            print(f"  {k}: array of shape {v.shape}, first few values: {v.flatten()[:5]}")
        else:
            print(f"  {k}: {v[:20]}..." if isinstance(v, bytes) else f"  {k}: {v}")

def main():
    # Initialize with security level 3
    params = DilithiumParams.get_params(security_level=3)
    
    # Generate keys
    print("\nGenerating keys...")
    start = time.time()
    keygen = KeyGenerator(params)
    public_key, private_key = keygen.generate_keypair()
    print(f"Key generation: {(time.time() - start)*1000:.2f}ms")
    
    # Print keys
    print_key("Public Key", public_key)
    print_key("Private Key", private_key)
    
    # Create and sign message
    message = b"Hello, Quantum-Resistant World!"
    print(f"\nOriginal message: {message.decode()}")
    
    signer = Signer(params)
    start = time.time()
    signature = signer.sign(message, private_key)
    print(f"Signing: {(time.time() - start)*1000:.2f}ms")
    
    # Print signature
    mu, z = signature
    print("\nSignature:")
    print(f"  mu: {mu[:20]}...")
    print(f"  z: array of shape {z.shape}, first few values: {z.flatten()[:5]}")
    
    # Verify signature
    verifier = Verifier(params)
    start = time.time()
    is_valid = verifier.verify(message, signature, public_key)
    print(f"Verification: {(time.time() - start)*1000:.2f}ms")
    
    print(f"\nSignature valid: {is_valid}")

if __name__ == "__main__":
    main() 