"""
Real Zomato API Integration for Food Discovery
Requires: ZOMATO_API_KEY in .env
"""

import requests
from typing import List, Optional
from app.config import ZOMATO_API_KEY, USER_LATITUDE, USER_LONGITUDE, USE_MOCK_SERVICES
from app.models import FoodOption

# Mock data when real API is not available
MOCK_RESTAURANTS = [
    FoodOption(
        restaurant="Sangeetha Veg",
        item="Idli + Dosa Combo",
        price=120,
        eta_minutes=15,
        eta_variance=3,
        rating=4.5,
        service="Swiggy"
    ),
    FoodOption(
        restaurant="MTR",
        item="Set Dosa + Sambar",
        price=150,
        eta_minutes=18,
        eta_variance=4,
        rating=4.7,
        service="Zomato"
    ),
    FoodOption(
        restaurant="Kaldan Continental",
        item="Chole Bhature",
        price=180,
        eta_minutes=20,
        eta_variance=5,
        rating=4.3,
        service="Swiggy"
    ),
]

def get_zomato_location_id(city: str = "Chennai") -> Optional[int]:
    """Get location ID from Zomato"""
    if not ZOMATO_API_KEY or USE_MOCK_SERVICES:
        return None
    
    try:
        headers = {"user-key": ZOMATO_API_KEY}
        response = requests.get(
            "https://api.zomato.com/api/v2.1/cities",
            headers=headers,
            params={"q": city},
            timeout=5
        )
        
        if response.status_code == 200:
            cities = response.json().get("city_results", [])
            if cities:
                return cities[0]["id"]
    except Exception as e:
        print(f"Error getting Zomato location: {e}")
    
    return None

def get_zomato_restaurants(cuisine: str = "South Indian", budget: int = 200) -> List[FoodOption]:
    """
    Fetch real restaurants from Zomato API
    
    Free tier includes:
    - Location search
    - Restaurant search with delivery info
    - User ratings
    
    Requires: ZOMATO_API_KEY environment variable
    """
    if not ZOMATO_API_KEY or USE_MOCK_SERVICES:
        print("Using mock food data. To use real Zomato API, add ZOMATO_API_KEY to .env")
        return MOCK_RESTAURANTS
    
    try:
        headers = {"user-key": ZOMATO_API_KEY}
        
        # Search by coordinates (Chennai center)
        response = requests.get(
            "https://api.zomato.com/api/v2.1/search",
            headers=headers,
            params={
                "lat": USER_LATITUDE,
                "lon": USER_LONGITUDE,
                "radius": 2000,  # 2km
                "sort": "rating",
                "order": "desc",
                "cuisines": cuisine,
                "delivery": 1  # Only delivery available
            },
            timeout=5
        )
        
        if response.status_code == 200:
            restaurants = response.json().get("restaurants", [])
            options = []
            
            for rest_data in restaurants[:5]:
                rest = rest_data.get("restaurant", {})
                
                # Filter by budget
                avg_cost = rest.get("average_cost_for_two", budget * 2)
                if avg_cost / 2 > budget:
                    continue
                
                # Extract delivery time from offers or estimate
                delivery_time = rest.get("delivery_time", 30)
                
                option = FoodOption(
                    restaurant=rest.get("name", "Unknown"),
                    item="Recommended Item",
                    price=float(rest.get("average_cost_for_two", 200) / 2),
                    eta_minutes=int(delivery_time),
                    eta_variance=2.0,
                    rating=float(rest.get("user_rating", {}).get("aggregate_rating", 0) or 4.0),
                    service="Zomato"
                )
                options.append(option)
            
            if options:
                return options
        
        print(f"Zomato API returned status {response.status_code}")
        
    except requests.exceptions.Timeout:
        print("Zomato API timeout - using mock data")
    except requests.exceptions.ConnectionError:
        print("No connection to Zomato API - using mock data")
    except Exception as e:
        print(f"Zomato API error: {e}")
    
    # Fallback to mock
    return MOCK_RESTAURANTS

def get_swiggy_restaurants(cuisine: str = "South Indian", budget: int = 200) -> List[FoodOption]:
    """
    Swiggy doesn't have an official public API
    
    Options:
    1. Use Zomato (they integrate with Swiggy restaurants)
    2. Contact Swiggy business team for partnership API
    3. Use unofficial reverse engineering (not recommended - violates ToS)
    
    For now, return empty - use Zomato instead
    """
    print("Swiggy API not available. Using Zomato as primary delivery service.")
    return []

def get_all_food_options(cuisine: str = "South Indian", budget: int = 200) -> List[FoodOption]:
    """Get combined options from available services"""
    
    # Try Zomato first
    options = get_zomato_restaurants(cuisine, budget)
    
    # Add Swiggy if available
    swiggy_options = get_swiggy_restaurants(cuisine, budget)
    options.extend(swiggy_options)
    
    # If nothing found, use mock
    if not options:
        options = MOCK_RESTAURANTS
    
    # Limit to top 3 by rating
    options.sort(key=lambda x: x.rating, reverse=True)
    return options[:3]

def get_food_option(cuisine: str = "South Indian") -> FoodOption:
    """Get best food option"""
    options = get_all_food_options(cuisine)
    return options[0] if options else MOCK_RESTAURANTS[0]

def create_zomato_order_link(restaurant_name: str, item: str) -> str:
    """
    Create a direct link to Zomato for ordering
    User clicks and completes order on Zomato
    """
    base_url = "https://www.zomato.com/search"
    return f"{base_url}?query={restaurant_name}"

# Future enhancement: Web scraping or alternative APIs
# For production, would need:
# - Official Swiggy partner API access
# - Uber Eats API integration
# - Direct payment integration
