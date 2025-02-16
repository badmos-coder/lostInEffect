from .core import DilithiumParams, PolynomialRing
from .sign import Signer
import numpy as np
from typing import Dict, Tuple, Optional

class Verifier:
    def __init__(self, params: DilithiumParams):
        self.params = params
        self.ring = PolynomialRing(params)
        self.signer = Signer(params)

    def verify(self, 
              message: bytes, 
              signature: Tuple[bytes, np.ndarray], 
              public_key: Dict) -> bool:
        """Verify signature against message and public key"""
        mu, z = signature
        
        # Check norm bounds
        if not self._check_bounds(z):
            return False
            
        # Compute w = Az - ct
        A = self.signer._sample_matrix(public_key['seed'])
        c = self.signer._challenge(mu, self._decompose(public_key['t']))
        
        w = np.zeros((self.params.k, self.params.n), dtype=np.int32)
        for i in range(self.params.k):
            for j in range(self.params.l):
                w[i] = self.ring.add(w[i], 
                    self.ring.multiply(A[i][j], z[j]))
            w[i] = self.ring.subtract(w[i], 
                self.ring.multiply(c, public_key['t'][i]))
        
        # Check if challenge matches
        w1 = self._decompose(w)
        c_prime = self.signer._challenge(mu, w1)
        
        return np.array_equal(c, c_prime)

    def _check_bounds(self, z: np.ndarray) -> bool:
        """Check if polynomial coefficients are within bounds"""
        return np.all(np.abs(z) < self.params.gamma1 - self.params.beta) 