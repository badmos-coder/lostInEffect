from adversarial import AdversarialDetector
from behavioral import BehavioralAnalytics
from fusion import MultiModalFusion
from risk import RealTimeRiskScorer
from quantum import QuantumResistantIntegration

class SecureBiometricSystem:
    def __init__(self):
        self.adversarial_detector = AdversarialDetector()
        self.behavioral_analytics = BehavioralAnalytics()
        self.fusion_engine = MultiModalFusion()
        self.risk_scorer = RealTimeRiskScorer()
        self.quantum_integration = QuantumResistantIntegration()

    def authenticate_user(self, user_id, biometric_data, context_data):
        results = {}

        # Adversarial check for face image
        face_image_path = biometric_data.get('face_image_path')
        if face_image_path:
            adversarial_check = self.adversarial_detector.detect_adversarial_attack(face_image_path)
            results['adversarial_check'] = adversarial_check
            if adversarial_check['is_adversarial']:
                return {
                    'authenticated': False,
                    'reason': 'Adversarial attack detected',
                    'results': results
                }

        # Behavioral analysis for fingerprint
        fingerprint_hex = biometric_data.get('fingerprint_hex')
        if fingerprint_hex:
            behavioral_analysis = self.behavioral_analytics.analyze_fingerprint_hex(fingerprint_hex)
            results['behavioral_analysis'] = behavioral_analysis
        else:
            behavioral_analysis = {"behavioral_score": 0.5} # Default score if no fingerprint

        # --- Mock Biometric Scores for Demonstration ---
        # In a real system, these would come from actual biometric matching engines.
        # For the CLI, we will use the behavioral score and add other mock scores.
        biometric_scores = {
            'fingerprint': behavioral_analysis.get('behavioral_score', 0.5),
            'face': 0.85, # Mock value
            'iris': 0.92, # Mock value
            'voice': 0.71, # Mock value
        }
        results['biometric_scores'] = biometric_scores

        # Fusion of scores
        fusion_score = self.fusion_engine.fuse_biometric_scores(
            biometric_scores, context_data
        )
        results['fusion_score'] = fusion_score

        # Risk assessment
        risk_assessment = self.risk_scorer.calculate_risk_score(
            user_id, context_data, fusion_score
        )
        results['risk_assessment'] = risk_assessment

        # Final decision logic
        authenticated = fusion_score > 0.6 and risk_assessment['overall_risk'] < 0.7
        results['final_decision'] = {
            'authenticated': authenticated,
            'confidence': fusion_score,
            'risk_level': risk_assessment['risk_level']
        }

        return results


if __name__ == "__main__":
    # This part is for basic testing. The main interaction will be via cli.py
    biometric_system = SecureBiometricSystem()

    user_id = "user_cli_test"
    
    # Simulate providing a real file path for the face
    # Create a dummy file for testing
    dummy_file_path = "/tmp/dummy_face.jpg"
    with open(dummy_file_path, "w") as f:
        f.write("dummy data")

    biometric_data = {
        'face_image_path': dummy_file_path,
        'fingerprint_hex': "ABCDEF1234567890" * 32 # A long, repeating hex string
    }

    context_data = {
        'location_change': True,
        'device_change': False,
        'network_change': False,
        'failed_attempts': 1,
        'lighting': 'good',
        'noise_level': 0.1
    }

    result = biometric_system.authenticate_user(user_id, biometric_data, context_data)
    import json
    print(json.dumps(result, indent=4))
