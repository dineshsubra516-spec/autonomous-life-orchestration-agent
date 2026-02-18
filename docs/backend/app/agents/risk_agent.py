class RiskAgent:
    def __init__(self, min_buffer=15, max_food_eta=30, max_travel_eta=20):
        self.min_buffer = min_buffer
        self.max_food_eta = max_food_eta
        self.max_travel_eta = max_travel_eta
    
    def evaluate(self, food, travel, context):
        """Evaluate risk of the proposed plan"""
        
        # Extract eta values, handling both dict and object formats
        food_eta = food.eta_minutes if hasattr(food, 'eta_minutes') else food.get("eta_minutes", 30)
        travel_eta = travel.eta_minutes if hasattr(travel, 'eta_minutes') else travel.get("eta_minutes", 15)
        food_variance = food.eta_variance if hasattr(food, 'eta_variance') else food.get("eta_variance", 2)
        travel_variance = travel.eta_variance if hasattr(travel, 'eta_variance') else travel.get("eta_variance", 2)
        
        total_eta = food_eta + travel_eta
        minutes_until_class = context.get("minutes_until_class", 60)
        buffer = minutes_until_class - total_eta
        
        # Base confidence
        confidence = 1.0
        reasoning = {
            "food_eta": food_eta,
            "travel_eta": travel_eta,
            "total_eta": total_eta,
            "minutes_until_class": minutes_until_class,
            "buffer": buffer
        }
        
        # Deductions based on constraints
        if buffer < self.min_buffer:
            confidence -= 0.35
            reasoning["buffer_risk"] = f"Buffer is {buffer} minutes, minimum required is {self.min_buffer}"
        
        if food_eta > self.max_food_eta:
            confidence -= 0.2
            reasoning["food_risk"] = f"Food ETA {food_eta} exceeds max {self.max_food_eta}"
        
        if travel_eta > self.max_travel_eta:
            confidence -= 0.2
            reasoning["travel_risk"] = f"Travel ETA {travel_eta} exceeds max {self.max_travel_eta}"
        
        if food_variance > 5:
            confidence -= 0.15
            reasoning["food_variance_risk"] = f"Food delivery has high variance {food_variance}"
        
        if travel_variance > 4:
            confidence -= 0.1
            reasoning["travel_variance_risk"] = f"Travel has variance {travel_variance}"
        
        # Ensure confidence is between 0 and 1
        confidence = max(0.0, min(1.0, confidence))
        
        return {
            "confidence": round(confidence, 2),
            "buffer_minutes": max(0, buffer),
            "reasoning": reasoning,
            "recommendation": "Safe to execute" if confidence >= 0.6 else "Needs user approval"
        }

