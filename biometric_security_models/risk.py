import time

class RealTimeRiskScorer:
    def __init__(self):
        self.historical_patterns = {}

    def calculate_risk_score(self, user_id, context_data, auth_score):
        context_risk = self._contextual_risk(context_data)
        time_risk = self._temporal_risk(user_id)

        # Simple weighted average for demonstration
        final_score = 0.6 * context_risk + 0.2 * time_risk + 0.2 * (1 - auth_score)
        final_score = max(0.0, min(1.0, final_score))

        return {
            "overall_risk": final_score,
            "details": {
                "contextual_risk": context_risk,
                "temporal_risk": time_risk,
                "authentication_score_impact": (1 - auth_score)
            },
            "risk_level": self._categorize(final_score)
        }

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
            # On first sight, assign a medium risk
            self.historical_patterns[user_id] = {'typical_hours': [hour]}
            return 0.4
        
        typical_hours = self.historical_patterns[user_id].get('typical_hours', [])
        if hour not in typical_hours:
            return 0.8 # High risk for unusual hour
        else:
            return 0.1 # Low risk for typical hour

    def _categorize(self, score):
        if score < 0.3: return "LOW"
        if score < 0.6: return "MEDIUM"
        if score < 0.8: return "HIGH"
        return "CRITICAL"
