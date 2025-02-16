from .core import DilithiumParams, PolynomialRing
import numpy as np
from typing import Tuple, Dict, Optional
from hashlib import shake_256

class Signer:
    def __init__(self, params: DilithiumParams):
        self.params = params
        self.ring = PolynomialRing(params)

    def _challenge(self, mu: bytes, w1: np.ndarray) -> np.ndarray:
        """Generate challenge polynomial c"""
        n, tau = self.params.n, self.params.tau
        
        # Hash message and w1
        shake = shake_256()
        shake.update(mu)
        for poly in w1:
            shake.update(poly.tobytes())
            
        # Generate sparse polynomial with tau +1/-1
        c = np.zeros(n, dtype=np.int32)
        positions = np.frombuffer(
            shake.digest(tau * 4), 
            dtype=np.int32
        ) % n
        signs = np.frombuffer(
            shake.digest(tau), 
            dtype=np.int8
        ) & 1
        
        for i, pos in enumerate(positions):
            c[pos] = 1 if signs[i] else -1
            
        return c

    def sign(self, message: bytes, private_key: Dict) -> Tuple[bytes, np.ndarray]:
        """Generate signature for message using private key"""
        # Unpack private key
        s1 = private_key['s1']
        s2 = private_key['s2']
        
        # Generate message digest
        mu = shake_256(message).digest(64)
        
        while True:
            # Sample y uniformly random
            y = np.array([
                np.random.randint(-self.params.gamma1, self.params.gamma1 + 1, 
                                size=self.params.n, dtype=np.int32)
                for _ in range(self.params.l)
            ])
            
            # Compute w = Ay
            w = np.zeros((self.params.k, self.params.n), dtype=np.int32)
            A = self._sample_matrix(private_key['seed'])
            
            for i in range(self.params.k):
                for j in range(self.params.l):
                    w[i] = self.ring.add(w[i], 
                        self.ring.multiply(A[i][j], y[j]))
            
            # Decompose w and compute challenge
            w1 = self._decompose(w)
            c = self._challenge(mu, w1)
            
            # Compute z = y + cs1
            z = y.copy()
            for i in range(self.params.l):
                z[i] = self.ring.add(z[i], 
                    self.ring.multiply(c, s1[i]))
            
            # Check if signature is valid
            if self._check_bounds(z) and self._check_bounds(w - c * private_key['t']):
                return mu, z

    def _decompose(self, w: np.ndarray) -> np.ndarray:
        """Decompose polynomial for high/low bits"""
        alpha = (self.params.q - 1) // (2 * self.params.gamma2)
        w1 = (w + self.params.gamma2) // (2 * self.params.gamma2)
        return w1

    def _check_bounds(self, x: np.ndarray) -> bool:
        """Check if polynomial coefficients are within bounds"""
        return np.all(np.abs(x) < self.params.gamma1 - self.params.beta) 