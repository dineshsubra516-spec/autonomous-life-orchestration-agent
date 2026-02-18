from datetime import datetime, timedelta
import pytz

class ScheduleAgent:
    def generate(self, user_prefs=None):
        """Generate daily schedule for a student in Chennai"""
        
        # Get current time in IST
        tz = pytz.timezone("Asia/Kolkata")
        now = datetime.now(tz)
        
        # Base schedule for students (modifiable based on preferences)
        schedule = [
            "9:00 AM - 1:00 PM: Core Lecture (Data Structures)",
            "1:00 PM - 2:00 PM: Lunch Break",
            "2:00 PM - 4:00 PM: Lab Session (Programming Lab)",
            "4:00 PM - 5:00 PM: Library / Study Time",
            "5:00 PM - 6:00 PM: Club Activity / Sports"
        ]
        
        # Add evening activities
        if now.hour < 18:
            schedule.extend([
                "6:00 PM - 7:30 PM: Dinner",
                "7:30 PM: Free Time / Project Work"
            ])
        else:
            schedule.append("Evening: Dinner & Personal Time")
        
        return schedule

