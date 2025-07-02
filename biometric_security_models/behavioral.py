import numpy as np
from tensorflow import keras
from keras import layers
from sklearn.ensemble import IsolationForest

class BehavioralAnalytics:
    def __init__(self):
        self.keystroke_model = self._keystroke_model()
        self.gait_model = self._gait_model()
        self.mouse_model = self._mouse_model()
        self.anomaly_detector = IsolationForest(contamination=0.1)

    def _keystroke_model(self):
        model = keras.Sequential([
            layers.LSTM(64, input_shape=(None, 5)),
            layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def _gait_model(self):
        model = keras.Sequential([
            layers.Conv1D(64, 3, activation='relu', input_shape=(100, 6)),
            layers.GlobalMaxPooling1D(),
            layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def _mouse_model(self):
        model = keras.Sequential([
            layers.Dense(32, activation='relu', input_shape=(10,)),
            layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def analyze_keystroke_dynamics(self, data):
        features = np.random.random((1, 10, 5))
        return self.keystroke_model.predict(features)[0][0]

    def analyze_gait_pattern(self, data):
        processed = np.random.random((1, 100, 6))
        return self.gait_model.predict(processed)[0][0]

    def detect_behavioral_anomalies(self, features):
        score = self.anomaly_detector.decision_function([features])[0]
        is_anomaly = self.anomaly_detector.predict([features])[0] == -1
        return {"is_anomaly": is_anomaly, "anomaly_score": score}
