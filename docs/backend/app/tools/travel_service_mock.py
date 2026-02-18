import requests
import json
from typing import List, Dict, Any
from app.config import USE_MOCK_SERVICES, UBER_API_KEY, OLA_API_KEY
from app.config import USER_LATITUDE, USER_LONGITUDE
from app.models import TravelOption

def get_uber_estimates(start_lat: float, start_lon: float, 
                       end_lat: float, end_lon: float) -> List[TravelOption]:
    """Fetch Uber ride estimates"""
    if not UBER_API_KEY or USE_MOCK_SERVICES:
        return get_mock_travel_options()
    
    try:
        headers = {
            "Authorization": f"Bearer {UBER_API_KEY}",
            "Accept-Language": "en_IN"
        }
        
        params = {
            "pickup_latitude": start_lat,
            "pickup_longitude": start_lon,
            "dropoff_latitude": end_lat,
            "dropoff_longitude": end_lon
        }
        
        response = requests.get(
            "https://api.uber.com/v1.2/estimates/price",
            headers=headers,
            params=params,
            timeout=5
        )
        
        if response.status_code == 200:
            prices = response.json().get("prices", [])
            options = []
            
            for price in prices:
                option = TravelOption(
                    service="Uber",
                    mode=price.get("display_name", "UberGo"),
                    cost=float(price.get("estimate", "0").split("-")[0].replace("$", "").strip() or "0") * 80,
                    eta_minutes=int(price.get("duration", 0) / 60) or 10,
                    eta_variance=2.0,
                    rating=4.7,
                )
                if option.cost > 0:
                    options.append(option)
            
            return options if options else get_mock_travel_options()
        
    except Exception as e:
        print(f"Error fetching Uber data: {e}")
    
    return get_mock_travel_options()


def get_ola_quotes(start_lat: float, start_lon: float,
                   end_lat: float, end_lon: float) -> List[TravelOption]:
    """Fetch Ola ride quotes"""
    if not OLA_API_KEY or USE_MOCK_SERVICES:
        return get_mock_travel_options()
    
    try:
        headers = {
            "Authorization": f"Bearer {OLA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "pickup_latitude": start_lat,
            "pickup_longitude": start_lon,
            "drop_latitude": end_lat,
            "drop_longitude": end_lon
        }
        
        response = requests.post(
            "https://api.olarides.com/v1/rides/estimates",
            headers=headers,
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            options = []
            
            for ride in data.get("rides", []):
                option = TravelOption(
                    service="Ola",
                    mode=ride.get("category", "Ride"),
                    cost=float(ride.get("amount", 0)),
                    eta_minutes=int(ride.get("eta", 10)),
                    eta_variance=1.5,
                    rating=4.6,
                )
                options.append(option)
            
            return options if options else get_mock_travel_options()
        
    except Exception as e:
        print(f"Error fetching Ola data: {e}")
    
    return get_mock_travel_options()


def get_mock_travel_options() -> List[TravelOption]:
    """Return realistic mock travel options for Chennai"""
    return [
        TravelOption(
            service="Ola",
            mode="Ride",
            cost=85,
            eta_minutes=7,
            eta_variance=2,
            rating=4.6
        ),
        TravelOption(
            service="Ola",
            mode="Auto",
            cost=55,
            eta_minutes=8,
            eta_variance=3,
            rating=4.4
        ),
        TravelOption(
            service="Uber",
            mode="UberGo",
            cost=120,
            eta_minutes=9,
            eta_variance=2,
            rating=4.7
        ),
        TravelOption(
            service="Uber",
            mode="UberX",
            cost=180,
            eta_minutes=8,
            eta_variance=1,
            rating=4.8
        ),
        TravelOption(
            service="Ola",
            mode="Bike",
            cost=40,
            eta_minutes=6,
            eta_variance=1,
            rating=4.5
        ),
    ]


def get_travel_option(start_lat: float = None, start_lon: float = None,
                     end_lat: float = None, end_lon: float = None) -> TravelOption:
    """Get a single recommended travel option"""
    start_lat = start_lat or USER_LATITUDE
    start_lon = start_lon or USER_LONGITUDE
    end_lat = end_lat or 12.9914  # IIT Madras
    end_lon = end_lon or 80.2303
    
    uber_options = get_uber_estimates(start_lat, start_lon, end_lat, end_lon)
    if uber_options:
        return uber_options[0]
    
    ola_options = get_ola_quotes(start_lat, start_lon, end_lat, end_lon)
    if ola_options:
        return ola_options[0]
    
    return TravelOption(
        service="Ola",
        mode="Ride",
        cost=85,
        eta_minutes=8,
        eta_variance=2,
        rating=4.6
    )


def get_all_travel_options(start_lat: float = None, start_lon: float = None,
                          end_lat: float = None, end_lon: float = None) -> List[TravelOption]:
    """Get multiple travel options"""
    start_lat = start_lat or USER_LATITUDE
    start_lon = start_lon or USER_LONGITUDE
    end_lat = end_lat or 12.9914  # IIT Madras
    end_lon = end_lon or 80.2303
    
    uber_options = get_uber_estimates(start_lat, start_lon, end_lat, end_lon)
    ola_options = get_ola_quotes(start_lat, start_lon, end_lat, end_lon)
    
    all_options = uber_options + ola_options
    return sorted(all_options, key=lambda x: x.eta_minutes)



