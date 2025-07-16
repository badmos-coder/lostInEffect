class BehavioralAnalytics:
    """
    Demonstration-focused behavioral analytics module.
    Uses rule-based checks on fingerprint hex data to provide plausible scores.
    """
    def analyze_fingerprint_hex(self, hex_string):
        """
        Analyzes a fingerprint hex string for demonstrable patterns.

        Args:
            hex_string (str): The fingerprint template as a hex string.

        Returns:
            dict: A dictionary with the analysis score and reasons.
        """
        score = 0.5  # Start with a neutral score
        reasons = []

        # Rule 1: Check length (a typical template has a certain size)
        hex_len = len(hex_string)
        if hex_len < 256 or hex_len > 1024:
            score -= 0.2
            reasons.append(f"Unusual hex string length ({hex_len} chars), which might indicate an anomaly.")
        else:
            score += 0.1
            reasons.append("Hex string length is within the expected range.")

        # Rule 2: Check for repeated patterns (real data is more random)
        # Look for long repeating character sequences
        has_repeating_pattern = False
        for i in range(len(hex_string) - 10):
            if hex_string[i:i+5] == hex_string[i+5:i+10]:
                has_repeating_pattern = True
                break
        
        if has_repeating_pattern:
            score -= 0.3
            reasons.append("Detected repeating patterns, which is uncommon in real fingerprint data.")
        else:
            score += 0.1
            reasons.append("No obvious repeating patterns found.")

        # Rule 3: Character distribution (a simple check)
        unique_chars = len(set(hex_string))
        if unique_chars < 10:
            score -= 0.2
            reasons.append(f"Very low character variety ({unique_chars} unique), suggesting low entropy.")

        final_score = max(0.0, min(1.0, score))

        return {
            "behavioral_score": final_score,
            "is_anomaly": final_score < 0.5,
            "details": {
                "analysis_reasons": reasons
            }
        }
