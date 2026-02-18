from datetime import datetime, timedelta
import pytz
from app.config import USER_TIMEZONE, USER_LATITUDE, USER_LONGITUDE

class ContextAgent:
    def gather(self, user_prefs=None):
        """Gather current context for a student in Chennai"""
        # Get current time in IST (Asia/Kolkata)
        tz = pytz.timezone(USER_TIMEZONE)
        now = datetime.now(tz)
        
        # Determine class start time (default 9 AM)
        class_start = user_prefs.get("class_start_time", "09:00") if user_prefs else "09:00"
        class_hour, class_minute = map(int, class_start.split(":"))
        
        # Calculate time until class
        class_time = now.replace(hour=class_hour, minute=class_minute, second=0, microsecond=0)
        
        # If class time is in the past, it's for tomorrow
        if class_time < now:
            class_time = class_time + timedelta(days=1)
        
        minutes_until_class = int((class_time - now).total_seconds() / 60)
        
        # Distance approximation (Indiranagar to IT college area in Chennai ~ 8-10 km)
        distance_km = user_prefs.get("distance_km", 8.5) if user_prefs else 8.5
        
        return {
            "current_time": now.strftime("%H:%M"),
            "timezone": USER_TIMEZONE,
            "date": now.strftime("%A, %B %d, %Y"),
            "minutes_until_class": max(minutes_until_class, 0),
            "distance_km": distance_km,
            "location_lat": USER_LATITUDE,
            "location_lon": USER_LONGITUDE,
            "class_location": user_prefs.get("class_location", "IIT Madras") if user_prefs else "IIT Madras",
            "weather": "Sunny"  # Could integrate with weather API
        }

