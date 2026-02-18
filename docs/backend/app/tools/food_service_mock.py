import requests
from typing import List, Dict, Any
from app.config import USE_MOCK_SERVICES, ZOMATO_API_KEY, USER_LATITUDE, USER_LONGITUDE
from app.models import FoodOption

def get_zomato_restaurants(cuisine: str = "South Indian", budget: int = 200) -> List[FoodOption]:
    """Fetch restaurants from Zomato API"""
    if not ZOMATO_API_KEY or USE_MOCK_SERVICES:
        return get_mock_food_options()
    
    try:
        headers = {"api_key": ZOMATO_API_KEY}
        params = {
            "lat": USER_LATITUDE,
            "lon": USER_LONGITUDE,
            "radius": 2000,
            "sort": "rating",
            "order": "desc"
        }
        
        response = requests.get(
            "https://api.zomato.com/api/v2.1/search",
            headers=headers,
            params=params,
            timeout=5
        )
        
        if response.status_code == 200:
            restaurants = response.json().get("restaurants", [])
            options = []
            
            for rest_data in restaurants[:5]:
                rest = rest_data.get("restaurant", {})
                option = FoodOption(
                    restaurant=rest.get("name", "Unknown"),
                    item="Recommended Item",
                    price=rest.get("average_cost_for_two", 200) / 2,
                    eta_minutes=int(rest.get("delivery_time", 30)),
                    eta_variance=2.0,
                    rating=float(rest.get("user_rating", {}).get("aggregate_rating", 4.0)),
                    service="Zomato"
                )
                options.append(option)
            
            return options if options else get_mock_food_options()
        
    except Exception as e:
        print(f"Error fetching Zomato data: {e}")
    
    return get_mock_food_options()


def get_swiggy_restaurants(cuisine: str = "South Indian", budget: int = 200) -> List[FoodOption]:
    """Fetch restaurants from Swiggy"""
    return get_mock_food_options()


def get_mock_food_options() -> List[FoodOption]:
    """Return mock food options for Chennai context - realistic variety"""
    return [
        FoodOption(
            restaurant="Sangeetha Veg Restaurant",
            item="Idli + Sambar + Chutney",
            price=110,
            eta_minutes=12,
            eta_variance=2,
            rating=4.6,
            service="Swiggy"
        ),
        FoodOption(
            restaurant="MTR (Madras Tiffin Restaurant)",
            item="Set Dosa + Sambar",
            price=130,
            eta_minutes=15,
            eta_variance=3,
            rating=4.8,
            service="Zomato"
        ),
        FoodOption(
            restaurant="Aachi Biryani",
            item="Chicken Biryani + Raita",
            price=180,
            eta_minutes=18,
            eta_variance=4,
            rating=4.5,
            service="Swiggy"
        ),
        FoodOption(
            restaurant="Dindigul Thalapakatti",
            item="Mutton Biryani Special",
            price=200,
            eta_minutes=20,
            eta_variance=2,
            rating=4.7,
            service="Zomato"
        ),
        FoodOption(
            restaurant="Kaldan Continental",
            item="Chole Bhature + Lassi",
            price=150,
            eta_minutes=16,
            eta_variance=3,
            rating=4.4,
            service="Swiggy"
        ),
        FoodOption(
            restaurant="Saravana Bhavan",
            item="Puri + Masala + Dosa",
            price=120,
            eta_minutes=13,
            eta_variance=2,
            rating=4.5,
            service="Zomato"
        ),
    ]


def get_food_option(cuisine: str = "South Indian") -> FoodOption:
    """Get a single recommended food option"""
    options = get_zomato_restaurants(cuisine)
    if options:
        return options[0]
    return get_mock_food_options()[0]


def get_all_food_options(budget: int = 200) -> List[FoodOption]:
    """Get multiple food options within budget"""
    all_options = get_zomato_restaurants(budget=budget)
    
    # Filter by budget
    filtered = [opt for opt in all_options if opt.price <= budget]
    
    return filtered if filtered else get_mock_food_options()


