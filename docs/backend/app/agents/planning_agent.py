class PlanningAgent:
    def create_plan(self, context, user_prefs=None):
        """Create an action plan based on context and preferences"""
        
        plan = {
            "objective": "Optimize morning routine for attending first class",
            "steps": [
                {
                    "order": 1,
                    "action": "Book food delivery",
                    "reason": "Need breakfast/meal before heading to class",
                    "budget_estimate": "150-200"
                },
                {
                    "order": 2,
                    "action": "Book travel",
                    "reason": f"Travel {context.get('distance_km', 8.5)}km to class at {context.get('class_location', 'campus')}",
                    "duration_estimate": f"{context.get('minutes_until_class', 60)} minutes available"
                },
                {
                    "order": 3,
                    "action": "Monitor time",
                    "reason": "Ensure timely arrival to first class",
                    "alert_threshold": "15 minutes before class"
                }
            ],
            "constraints": [
                f"Must arrive before {user_prefs.get('class_start_time', '09:00')} AM" if user_prefs else "Must arrive by 9:00 AM",
                "Stay within budget",
                "Minimize delivery delay variance"
            ]
        }
        
        return plan

