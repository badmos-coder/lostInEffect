from .core import DilithiumParams, PolynomialRing
import numpy as np
from typing import Tuple, Dict
import secrets
from hashlib import shake_256

class KeyGenerator:
    def __init__(self, params: DilithiumParams):
        self.params = params
        self.ring = PolynomialRing(params)

    def _sample_matrix(self, seed: bytes) -> np.ndarray:
        """Sample matrix A uniformly random from seed"""
        k, l = self.params.k, self.params.l
        n, q = self.params.n, self.params.q
        
        # Use SHAKE-256 for expansion
        shake = shake_256(seed)
        matrix = np.zeros((k, l, n), dtype=np.int32)
        
        for i in range(k):
            for j in range(l):
                # Generate coefficients for each polynomial
                coeffs = np.frombuffer(
                    shake.digest(n * 4), 
                    dtype=np.int32
                ) % q
                matrix[i][j] = coeffs
                shake = shake_256(shake.digest(32))
        
        return matrix

    def _sample_small(self, seed: bytes) -> np.ndarray:
        """Sample small polynomials with coefficients in [-η, η]"""
        n, eta = self.params.n, self.params.eta
        shake = shake_256(seed)
        coeffs = np.frombuffer(shake.digest(n), dtype=np.int8)
        return (coeffs % (2 * eta + 1)) - eta

    def generate_keypair(self) -> Tuple[Dict, Dict]:
        """Generate public and private keys"""
        # Generate random seed
        seed = secrets.token_bytes(32)
        
        # Generate matrix A
        A = self._sample_matrix(seed)
        
        # Sample small polynomials for secret key
        s1 = np.array([self._sample_small(seed + bytes([i])) 
                      for i in range(self.params.l)])
        s2 = np.array([self._sample_small(seed + bytes([i + self.params.l])) 
                      for i in range(self.params.k)])
        
        # Compute t = As1 + s2
        t = np.zeros((self.params.k, self.params.n), dtype=np.int32)
        for i in range(self.params.k):
            for j in range(self.params.l):
                t[i] = self.ring.add(t[i], 
                    self.ring.multiply(A[i][j], s1[j]))
            t[i] = self.ring.add(t[i], s2[i])

        # Create key pairs
        public_key = {
            'seed': seed,
            't': t
        }
        
        private_key = {
            'seed': seed,
            's1': s1,
            's2': s2,
            't': t
        }
        
        return public_key, private_key 