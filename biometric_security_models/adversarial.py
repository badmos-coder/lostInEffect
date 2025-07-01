import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from utils import preprocess_image


class AdversarialDetector:
    def __init__(self):
        self.detector_model = self._build_discriminator()
        self.perturbation_analyzer = self._build_perturbation_analyzer()

    def _build_discriminator(self):
        model = keras.Sequential([
            layers.Conv2D(64, 3, activation='relu', input_shape=(224, 224, 3)),
            layers.MaxPooling2D(),
            layers.Conv2D(128, 3, activation='relu'),
            layers.GlobalAveragePooling2D(),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def _build_perturbation_analyzer(self):
        model = keras.Sequential([
            layers.Input(shape=(224, 224, 3)),
            layers.Conv2D(32, 3, activation='relu'),
            layers.GlobalAveragePooling2D(),
            layers.Dense(64, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def detect_adversarial_attack(self, biometric_data):
        processed = preprocess_image(biometric_data)

        synthetic_score = self.detector_model.predict(processed)[0][0]
        perturbation_score = self.perturbation_analyzer.predict(processed)[0][0]
        threat_score = (synthetic_score + perturbation_score) / 2

        return {
            "is_adversarial": threat_score > 0.7,
            "confidence": threat_score,
            "synthetic_probability": synthetic_score,
            "perturbation_probability": perturbation_score
        }
