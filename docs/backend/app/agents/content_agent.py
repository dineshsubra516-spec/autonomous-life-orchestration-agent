from datetime import datetime


class ContextAgent:
    def gather(self):
        now = datetime.now()
        return {
            "current_time": now.strftime("%H:%M"),
            "minutes_until_class": 60,
            "distance_km": 2.5
        }
