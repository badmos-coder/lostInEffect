import time
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers


class RealTimeRiskScorer:
    def __init__(self):
        self.model = self._build_model()
        self.historical_patterns = {}

    def _build_model(self):
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(20,)),
            layers.Dense(64, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def calculate_risk_score(self, user_id, biometric_data, context_data, auth_score):
        features = self._extract_features(user_id, context_data, auth_score)
        ml_score = self.model.predict(features)[0][0]
        context_risk = self._contextual_risk(context_data)
        time_risk = self._temporal_risk(user_id)

        final_score = 0.5 * ml_score + 0.3 * context_risk + 0.2 * time_risk
        return {
            "overall_risk": final_score,
            "ml_risk": ml_score,
            "contextual_risk": context_risk,
            "temporal_risk": time_risk,
            "risk_level": self._categorize(final_score)
        }

    def _extract_features(self, user_id, context, auth_score):
        hour = time.localtime().tm_hour
        features = [
            auth_score,
            hour / 24.0,
            int(9 <= hour <= 17),
            int(hour < 6 or hour > 22),
            context.get('location_change', 0),
            context.get('device_change', 0),
            context.get('network_change', 0),
            context.get('failed_attempts', 0) / 10.0
        ]
        while len(features) < 20:
            features.append(0.0)
        return np.array(features[:20]).reshape(1, -1)

    def _contextual_risk(self, context):
        risk = 0
        if context.get('location_change'): risk += 0.3
        if context.get('device_change'): risk += 0.4
        if context.get('network_change'): risk += 0.2
        risk += min(context.get('failed_attempts', 0) * 0.1, 0.5)
        return min(risk, 1.0)

    def _temporal_risk(self, user_id):
        hour = time.localtime().tm_hour
        if user_id not in self.historical_patterns:
            return 0.5
        typical = self.historical_patterns[user_id].get('typical_hours', [])
        return 0.1 if hour in typical else 0.8

    def _categorize(self, score):
        if score < 0.3: return "LOW"
        if score < 0.6: return "MEDIUM"
        if score < 0.8: return "HIGH"
        return "CRITICAL"
