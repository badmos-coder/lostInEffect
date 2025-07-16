import os

class AdversarialDetector:
    """
    Demonstration-focused adversarial detector.
    Instead of a trained model, it uses rule-based checks on file metadata
    to provide plausible, interactive results for a CLI tool.
    """
    def detect_adversarial_attack(self, image_path):
        """
        Analyzes metadata of a given image file to determine if it might be synthetic.

        Args:
            image_path (str): The file path to the face image.

        Returns:
            dict: A dictionary containing the analysis results.
        """
        try:
            file_size = os.path.getsize(image_path)
            file_name = os.path.basename(image_path)
        except FileNotFoundError:
            return {
                "error": "File not found.",
                "is_adversarial": True,
                "confidence": 1.0,
                "reason": "The image file does not exist."
            }

        synthetic_score = 0.0
        perturbation_score = 0.0
        reasons = []

        # Rule 1: Unusually small file size (potential sign of a simple synthetic image)
        if file_size < 10 * 1024:  # Less than 10 KB
            synthetic_score += 0.4
            reasons.append(f"File size is very small ({file_size / 1024:.2f} KB), which can be a sign of a non-standard image.")

        # Rule 2: Generic file name (often used in generated datasets)
        if 'generated' in file_name.lower() or 'synthetic' in file_name.lower():
            synthetic_score += 0.6
            reasons.append("File name contains keywords like 'generated' or 'synthetic'.")

        # Rule 3: Check for signs of perturbation (e.g., file name hints)
        if 'perturbed' in file_name.lower() or 'attack' in file_name.lower():
            perturbation_score += 0.7
            reasons.append("File name contains keywords suggesting it's a test attack sample.")
        
        # Normalize scores
        synthetic_score = min(synthetic_score, 1.0)
        perturbation_score = min(perturbation_score, 1.0)

        threat_score = (synthetic_score + perturbation_score) / 2

        return {
            "is_adversarial": threat_score > 0.5,
            "confidence": float(threat_score),
            "details": {
                "synthetic_probability": float(synthetic_score),
                "perturbation_probability": float(perturbation_score),
                "analysis_reasons": reasons if reasons else ["No obvious signs of adversarial attack detected based on metadata."]
            }
        }
