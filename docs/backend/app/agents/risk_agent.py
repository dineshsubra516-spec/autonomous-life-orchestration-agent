class RiskAgent:
    def evaluate(self, food, travel, context):
        total_eta = food["eta_minutes"] + travel["eta_minutes"]
        buffer = context["minutes_until_class"] - total_eta

        confidence = 1.0
        if buffer < 15:
            confidence -= 0.3
        if food["eta_variance"] > 5:
            confidence -= 0.2
        if travel["eta_variance"] > 5:
            confidence -= 0.2

        confidence = max(confidence, 0.0)

        return {
            "confidence": round(confidence, 2),
            "buffer_minutes": buffer
        }
