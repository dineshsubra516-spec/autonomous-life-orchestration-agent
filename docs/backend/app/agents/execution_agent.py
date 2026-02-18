from datetime import datetime
import pytz

class ExecutionAgent:
    def execute(self, food, travel, user_prefs=None):
        """Execute the booking for food and travel"""
        
        # Extract data, handling both dict and object formats
        if hasattr(food, 'restaurant'):
            food_name = f"{food.item} from {food.restaurant}"
            food_service = food.service
        else:
            food_name = food.get("item", "Food item")
            food_service = food.get("service", "Service")
        
        if hasattr(travel, 'mode'):
            travel_mode = f"{travel.service} {travel.mode}"
            travel_cost = travel.cost
        else:
            travel_mode = travel.get("mode", "Transport")
            travel_cost = travel.get("cost", 0)
        
        # Get current time in IST
        tz = pytz.timezone("Asia/Kolkata")
        now = datetime.now(tz)
        
        return {
            "food_ordered": food_name,
            "food_service": food_service,
            "travel_booked": travel_mode,
            "travel_cost": travel_cost,
            "confirmation_time": now.strftime("%H:%M:%S"),
            "status": "Confirmed",
            "notes": "Booking details would be sent to registered phone number"
        }

