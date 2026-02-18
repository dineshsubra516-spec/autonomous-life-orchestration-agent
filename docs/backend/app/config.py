import os
from dotenv import load_dotenv

load_dotenv()

# API Keys and Configuration
ZOMATO_API_KEY = os.getenv("ZOMATO_API_KEY", "")
SWIGGY_API_KEY = os.getenv("SWIGGY_API_KEY", "")
UBER_API_KEY = os.getenv("UBER_API_KEY", "")
OLA_API_KEY = os.getenv("OLA_API_KEY", "")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# User Location - Chennai by default
USER_CITY = "Chennai"
USER_STATE = "Tamil Nadu"
USER_COUNTRY = "India"
USER_TIMEZONE = "Asia/Kolkata"  # IST
USER_LATITUDE = 13.0827  # Default Chennai coordinates
USER_LONGITUDE = 80.2707

# Service Preferences
FOOD_DELIVERY_PREFERENCES = ["Swiggy", "Zomato"]
TRAVEL_PREFERENCES = ["Ola", "Uber"]

# Agent Configuration
CONFIDENCE_THRESHOLD = 0.6
MAX_FOOD_ETA = 30  # minutes
MAX_TRAVEL_ETA = 20  # minutes
MIN_BUFFER_TIME = 15  # minutes before class

# Use mock services if real APIs are not available
USE_MOCK_SERVICES = not (ZOMATO_API_KEY and SWIGGY_API_KEY and UBER_API_KEY)
