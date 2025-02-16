import numpy as np
from typing import Tuple, List, Optional
from hashlib import shake_256
import secrets

class DilithiumParams:
    """Dilithium parameter sets"""
    def __init__(self, k: int, l: int, eta: int, gamma1: int, gamma2: int, tau: int, d: int, q: int = 8380417):
        self.k = k          # Number of rows of A
        self.l = l          # Number of rows of secret keys
        self.eta = eta      # Coefficient range for secret keys
        self.gamma1 = gamma1  # Parameter for rounding
        self.gamma2 = gamma2  # Parameter for rounding
        self.tau = tau      # Number of +/- 1's in challenge
        self.d = d          # Dropped bits in rounding
        self.q = q          # Modulus (prime)
        self.n = 256        # Polynomial degree (fixed for Dilithium)
        self.beta = gamma1 // 4  # Changed from gamma1 // 2

    @classmethod
    def get_params(cls, security_level: int = 3) -> 'DilithiumParams':
        """Get parameters for different security levels (2, 3, or 5)"""
        if security_level == 2:
            return cls(k=4, l=4, eta=2, gamma1=2**17, gamma2=2**17, tau=39, d=13)
        elif security_level == 3:
            return cls(k=6, l=5, eta=4, gamma1=2**17, gamma2=2**17, tau=49, d=13)
        elif security_level == 5:
            return cls(k=8, l=7, eta=2, gamma1=2**17, gamma2=2**17, tau=60, d=13)
        else:
            raise ValueError("Security level must be 2, 3, or 5")

    def multiply(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Multiply two polynomials in R_q"""
        result = np.zeros(self.n, dtype=np.int64)  # Change to int64
        for i in range(self.n):
            for j in range(self.n):
                k = (i + j) % self.n
                if j >= self.n//2:
                    result[k] = (result[k] - (a[i].astype(np.int64) * b[j])) % self.q
                else:
                    result[k] = (result[k] + (a[i].astype(np.int64) * b[j])) % self.q
        return result.astype(np.int32)

class PolynomialRing:
    """Operations in R_q = Z_q[X]/(X^n + 1)"""
    def __init__(self, params: DilithiumParams):
        self.params = params
        self.n = params.n
        self.q = params.q

    def add(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Add two polynomials in R_q"""
        return (a + b) % self.q

    def subtract(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Subtract two polynomials in R_q"""
        return (a - b) % self.q

    def multiply(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Vectorized polynomial multiplication mod (X^n + 1)"""
        a = a.astype(np.int64)
        b = b.astype(np.int64)
        
        # Use matrix multiplication for faster computation
        result = np.zeros(self.n, dtype=np.int64)
        b_matrix = np.zeros((self.n, self.n), dtype=np.int64)
        
        # Create negacyclic matrix
        for i in range(self.n):
            b_matrix[i] = np.roll(b, i)
            if i > 0:
                b_matrix[i, :i] = -b_matrix[i, :i]
        
        result = (a @ b_matrix) % self.q
        return result.astype(np.int32) 