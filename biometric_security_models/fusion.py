from tensorflow import keras
from tensorflow.keras import layers


class MultiModalFusion:
    def __init__(self):
        self.confidence_weights = {
            'fingerprint': 0.3,
            'face': 0.25,
            'iris': 0.2,
            'voice': 0.15,
            'behavioral': 0.1
        }

    def fuse_biometric_scores(self, biometric_scores, context_info=None):
        weights = self.adjust_weights_by_context(context_info) if context_info else self.confidence_weights
        total = sum(score * weights.get(mod, 0) for mod, score in biometric_scores.items())
        return total

    def adjust_weights_by_context(self, context):
        weights = self.confidence_weights.copy()
        if context.get('lighting') == 'poor':
            weights['face'] *= 0.7
            weights['iris'] *= 0.8
            weights['fingerprint'] *= 1.2
        if context.get('noise_level', 0) > 0.7:
            weights['voice'] *= 0.6
            weights['behavioral'] *= 1.3

        total = sum(weights.values())
        return {k: v / total for k, v in weights.items()}
