from dilithium.core import DilithiumParams
from dilithium.keygen import KeyGenerator
from dilithium.sign import Signer
from dilithium.verify import Verifier

def main():
    # Initialize with security level 3
    params = DilithiumParams.get_params(security_level=3)
    
    # Generate keys
    keygen = KeyGenerator(params)
    public_key, private_key = keygen.generate_keypair()
    
    # Create message and sign it
    message = b"Hello, Quantum-Resistant World!"
    signer = Signer(params)
    signature = signer.sign(message, private_key)
    
    # Verify signature
    verifier = Verifier(params)
    is_valid = verifier.verify(message, signature, public_key)
    
    print(f"Message: {message.decode()}")
    print(f"Signature valid: {is_valid}")

if __name__ == "__main__":
    main() 