from dilithium.core import DilithiumParams, PolynomialRing
from dilithium.keygen import KeyGenerator
import numpy as np
from typing import Tuple, Dict, Optional
from hashlib import shake_256

class Signer:
    def __init__(self, params: DilithiumParams):
        self.params = params
        self.ring = PolynomialRing(params)
        self.keygen = KeyGenerator(params)

    def _challenge(self, mu: bytes, w: np.ndarray) -> np.ndarray:
        """Generate challenge polynomial c"""
        shake = shake_256()
        shake.update(mu)
        
        # Ensure w is properly normalized and formatted
        w_norm = w.copy()
        for i in range(len(w)):
            w_norm[i] = w_norm[i] % self.params.q
        w_bytes = w_norm.astype(np.int32).tobytes()
        shake.update(w_bytes)
        
        # Generate challenge polynomial
        c = np.zeros(self.params.n, dtype=np.int32)
        digest = shake.digest(self.params.tau * 4)
        positions = np.frombuffer(digest, dtype=np.int32)
        
        # Set tau positions to ±1
        used_positions = set()
        pos_idx = 0
        while len(used_positions) < self.params.tau and pos_idx < len(positions):
            pos = positions[pos_idx] % self.params.n
            if pos not in used_positions:
                c[pos] = 1  # Using consistent sign for simplicity
                used_positions.add(pos)
            pos_idx += 1
            
        return c

    def _decompose(self, w: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Decompose polynomial into high and low bits"""
        # Center around 0
        w = np.where(w >= self.params.q//2,
                    w - self.params.q,
                    w)
        
        # Calculate decomposition parameters
        alpha = (self.params.q - 1) // (2 * self.params.gamma2)
        
        # High bits
        w1 = np.round(w / (2 * self.params.gamma2))
        w1 = w1.astype(np.int32)
        
        # Low bits
        w0 = w - w1 * (2 * self.params.gamma2)
        
        return w1, w0

    def sign(self, message: bytes, private_key: Dict) -> Tuple[bytes, np.ndarray]:
        """Generate signature for message using private key"""
        while True:  # Keep trying until we get valid z
            mu = shake_256(message).digest(32)
            
            # Sample y with smaller bounds
            y = np.array([
                np.random.randint(-self.params.gamma1 + self.params.beta, 
                                self.params.gamma1 - self.params.beta + 1, 
                                size=self.params.n, dtype=np.int32)
                for _ in range(self.params.l)
            ])
            
            A = self.keygen._sample_matrix(private_key['seed'])
            w = np.zeros((self.params.k, self.params.n), dtype=np.int32)
            
            # Compute w = Ay
            for i in range(self.params.k):
                for j in range(self.params.l):
                    w[i] = (w[i] + self.ring.multiply(A[i][j], y[j])) % self.params.q
            
            # Decompose w and check bounds
            w1_arr = []
            for i in range(self.params.k):
                w1, w0 = self._decompose(w[i])
                if np.any(np.abs(w1) >= self.params.gamma2):
                    break
                w1_arr.append(w1)
            else:
                c = self._challenge(mu, np.array(w1_arr))
                
                # Compute z = y + cs1
                z = y.copy()
                for i in range(self.params.l):
                    cs1 = self.ring.multiply(c, private_key['s1'][i])
                    z[i] = (z[i] + cs1) % self.params.q
                    
                    # Center around 0
                    z[i] = np.where(z[i] >= self.params.q//2,
                                   z[i] - self.params.q,
                                   z[i])
                    
                    # Check bounds
                    if np.any(np.abs(z[i]) >= self.params.gamma1 - self.params.beta):
                        break
                else:
                    # All checks passed
                    return mu, z
            continue  # Try again with new y

    def _check_bounds(self, x: np.ndarray) -> bool:
        """Check if polynomial coefficients are within bounds"""
        return np.all(np.abs(x) < self.params.gamma1 - self.params.beta) 