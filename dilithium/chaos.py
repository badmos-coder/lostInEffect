import numpy as np
from typing import List, Tuple, Dict
from hashlib import sha256, shake_256
import secrets
from dilithium.core import DilithiumParams
from dilithium.keygen import KeyGenerator
from dilithium.sign import Signer
from dilithium.verify import Verifier

class LorenzEncryption:
    def __init__(self, seed: bytes):
        # Lorenz system parameters
        self.sigma = 10.0
        self.rho = 28.0
        self.beta = 8.0/3.0
        self.dt = 0.01
        self.seed = seed
        
    def _generate_initial_conditions(self, nonce: bytes) -> Tuple[float, float, float]:
        """Generate initial conditions from seed and nonce"""
        # Combine seed and nonce
        hash_input = self.seed + nonce
        hash_value = sha256(hash_input).hexdigest()
        
        # Generate three different initial conditions
        x0 = int(hash_value[:16], 16) / (16 ** 16)
        y0 = int(hash_value[16:32], 16) / (16 ** 16)
        z0 = int(hash_value[32:48], 16) / (16 ** 16)
        
        # Scale to appropriate range for Lorenz system
        return (x0 * 40 - 20, y0 * 40 - 20, z0 * 40 - 20)

    def _lorenz_system(self, steps: int, nonce: bytes) -> np.ndarray:
        """Generate Lorenz chaotic sequence"""
        x, y, z = self._generate_initial_conditions(nonce)
        sequence = np.zeros((steps, 3), dtype=np.float64)
        
        # Run Lorenz system
        for i in range(steps):
            dx = self.sigma * (y - x)
            dy = x * (self.rho - z) - y
            dz = x * y - self.beta * z
            
            x += dx * self.dt
            y += dy * self.dt
            z += dz * self.dt
            
            sequence[i] = [x, y, z]
            
        return sequence

    def _generate_keystream(self, length: int, nonce: bytes) -> bytes:
        """Generate keystream from Lorenz system"""
        # Generate more steps for better mixing
        extra_steps = 1000
        sequence = self._lorenz_system(length + extra_steps, nonce)
        
        # Use all three coordinates and discard initial values
        keystream = []
        for x, y, z in sequence[extra_steps:]:
            # Combine all coordinates for better randomness
            val = (abs(x) + abs(y) + abs(z)) % 256
            keystream.append(int(val))
            
        return bytes(keystream)

    def encrypt(self, plaintext: bytes) -> Tuple[bytes, bytes]:
        """Encrypt data using enhanced Lorenz system"""
        # Generate random nonce
        nonce = secrets.token_bytes(16)
        
        # Generate keystream
        keystream = self._generate_keystream(len(plaintext), nonce)
        
        # XOR with plaintext
        ciphertext = bytes(a ^ b for a, b in zip(plaintext, keystream))
        
        # Add authentication tag using SHAKE-256
        auth_input = nonce + ciphertext + self.seed
        auth_tag = shake_256(auth_input).digest(32)
        
        # Return ciphertext and nonce separately
        return ciphertext + auth_tag, nonce

    def decrypt(self, cipherdata: bytes, nonce: bytes) -> bytes:
        """Decrypt data using enhanced Lorenz system"""
        # Split input into components
        auth_tag = cipherdata[-32:]
        ciphertext = cipherdata[:-32]
        
        # Verify authentication tag
        auth_input = nonce + ciphertext + self.seed
        expected_tag = shake_256(auth_input).digest(32)
        if not secrets.compare_digest(auth_tag, expected_tag):
            raise ValueError("Authentication failed")
        
        # Generate keystream
        keystream = self._generate_keystream(len(ciphertext), nonce)
        
        # XOR with ciphertext
        return bytes(a ^ b for a, b in zip(ciphertext, keystream))

class HybridEncryption:
    """Combines Dilithium signatures with Lorenz encryption"""
    
    def __init__(self, dilithium_params: DilithiumParams):
        self.params = dilithium_params
        self.keygen = KeyGenerator(dilithium_params)
        self.signer = Signer(dilithium_params)
        self.verifier = Verifier(dilithium_params)
        
    def generate_keys(self) -> Tuple[Dict, Dict]:
        """Generate Dilithium key pair"""
        try:
            print("Generating Dilithium key pair...")
            # Generate key pair using Dilithium
            public_key, private_key = self.keygen.generate_keypair()
            
            print(f"Generated public key with components: {list(public_key.keys())}")
            print(f"Generated private key with components: {list(private_key.keys())}")
            
            return public_key, private_key
            
        except Exception as e:
            raise RuntimeError(f"Key generation failed: {str(e)}")

    def encrypt_and_sign(self, message: bytes, private_key: Dict) -> Tuple[bytes, bytes, Tuple]:
        """Encrypt message and sign the ciphertext"""
        try:
            # Initialize Lorenz with private key seed
            lorenz = LorenzEncryption(private_key['seed'])
            
            # Log encryption process
            print("Starting hybrid encryption process:")
            print(f"1. Message size: {len(message)} bytes")
            
            # Encrypt message with Lorenz chaos
            ciphertext, nonce = lorenz.encrypt(message)
            print(f"2. Generated ciphertext size: {len(ciphertext)} bytes")
            print(f"3. Generated nonce size: {len(nonce)} bytes")
            
            # Sign ciphertext using Dilithium
            signature = self.signer.sign(ciphertext, private_key)
            print("4. Generated Dilithium signature")
            print(f"   - Mu size: {len(signature[0])} bytes")
            print(f"   - Z shape: {signature[1].shape}")
            
            # Verify signature immediately as a check
            if not self.verifier.verify(ciphertext, signature, private_key):
                raise ValueError("Signature verification failed immediately after signing")
            print("5. Verified signature successfully")
            
            return ciphertext, nonce, signature
            
        except Exception as e:
            raise RuntimeError(f"Encryption failed: {str(e)}")

    def verify_and_decrypt(self, ciphertext: bytes, nonce: bytes, 
                          signature: Tuple, public_key: Dict) -> bytes:
        """Verify signature and decrypt message"""
        try:
            print("\nStarting hybrid decryption process:")
            print(f"1. Received ciphertext size: {len(ciphertext)} bytes")
            print(f"2. Received nonce size: {len(nonce)} bytes")
            print("3. Verifying Dilithium signature...")
            
            # Verify signature first
            if not self.verifier.verify(ciphertext, signature, public_key):
                raise ValueError("Signature verification failed")
            print("4. Signature verified successfully")
            
            # Initialize Lorenz with public key seed
            lorenz = LorenzEncryption(public_key['seed'])
            print("5. Initialized Lorenz system with public key seed")
            
            # Decrypt message
            decrypted = lorenz.decrypt(ciphertext, nonce)
            print(f"6. Decrypted message size: {len(decrypted)} bytes")
            
            # Verify decryption succeeded
            try:
                decrypted.decode('utf-8')
                print("7. Successfully decoded message as UTF-8")
            except UnicodeDecodeError:
                raise ValueError("Decryption failed - output is not valid UTF-8")
                
            return decrypted
            
        except Exception as e:
            raise RuntimeError(f"Decryption failed: {str(e)}") 