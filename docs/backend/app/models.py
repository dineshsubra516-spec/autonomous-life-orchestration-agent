from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class UserPreferences(BaseModel):
    location: str = "Indiranagar, Bangalore"
    food_budget: int = 200
    cuisine_preferences: List[str] = ["South Indian", "Fast Food", "Continental"]
    dietary_restrictions: List[str] = []
    travel_preference: str = "fastest"  # fastest, cheapest, eco-friendly
    home_latitude: float = 13.0827
    home_longitude: float = 80.2707
    class_latitude: float = 13.1939
    class_longitude: float = 80.1180
    class_start_time: str = "09:00"
    timezone: str = "Asia/Kolkata"

class FoodOption(BaseModel):
    restaurant: str
    item: str
    price: float
    eta_minutes: int
    eta_variance: float
    rating: float
    service: str  # "Swiggy" or "Zomato"

class TravelOption(BaseModel):
    service: str  # "Ola" or "Uber"
    mode: str  # "Ride", "Premium", "XL"
    cost: float
    eta_minutes: int
    eta_variance: float
    rating: float

class ExecutionRecord(BaseModel):
    timestamp: datetime
    food_ordered: Optional[str]
    travel_booked: Optional[str]
    confidence: float
    buffer_minutes: int
    status: str  # "executed", "waiting_approval", "failed"
    notes: str = ""

class AgentDecision(BaseModel):
    state: str
    confidence: float
    buffer_minutes: int
    food_options: List[FoodOption]
    travel_options: List[TravelOption]
    recommended_food: Optional[FoodOption]
    recommended_travel: Optional[TravelOption]
    message: Optional[str]
    reasoning: Dict[str, Any]
