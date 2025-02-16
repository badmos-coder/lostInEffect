from dilithium.core import DilithiumParams, PolynomialRing
from dilithium.keygen import KeyGenerator
from dilithium.sign import Signer
import numpy as np
from typing import Dict, Tuple

class Verifier:
    def __init__(self, params: DilithiumParams):
        self.params = params
        self.ring = PolynomialRing(params)
        self.keygen = KeyGenerator(params)
        self.signer = Signer(params)

    def verify(self, message: bytes, signature: Tuple[bytes, np.ndarray], public_key: Dict) -> bool:
        """Verify signature against message and public key"""
        try:
            mu, z = signature
            
            # Check z bounds
            if not np.all(np.abs(z) < self.params.gamma1):
                print("Z bounds check failed")
                return False
            
            # Compute Az
            A = self.keygen._sample_matrix(public_key['seed'])
            w = np.zeros((self.params.k, self.params.n), dtype=np.int32)
            
            # Compute w = Az
            for i in range(self.params.k):
                for j in range(self.params.l):
                    w[i] = (w[i] + self.ring.multiply(A[i][j], z[j])) % self.params.q
            
            # Decompose w for challenge
            w1_arr = []
            for i in range(self.params.k):
                w1, _ = self.signer._decompose(w[i])
                w1_arr.append(w1)
            
            c = self.signer._challenge(mu, np.array(w1_arr))
            
            # Compute w' = Az - ct
            for i in range(self.params.k):
                ct = self.ring.multiply(c, public_key['t'][i])
                w[i] = (w[i] - ct) % self.params.q
                
                # Center around 0
                w[i] = np.where(w[i] >= self.params.q//2,
                               w[i] - self.params.q,
                               w[i])
                
                # Decompose and check bounds
                w1, _ = self.signer._decompose(w[i])
                if np.any(np.abs(w1) >= self.params.gamma2):
                    print("High bits check failed")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Verification error: {e}")
            return False 