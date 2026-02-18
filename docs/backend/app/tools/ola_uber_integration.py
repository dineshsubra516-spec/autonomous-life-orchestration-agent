"""
Real Ola & Uber Ride Integration
Supports autonomous booking with user's saved payment method
"""

import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import (
    OLA_API_KEY, UBER_API_KEY, 
    USER_LATITUDE, USER_LONGITUDE,
    USE_MOCK_SERVICES
)
from app.models import TravelOption

MOCK_OPTIONS = [
    TravelOption(
        service="Ola",
        mode="Ride",
        cost=95,
        eta_minutes=8,
        eta_variance=2,
        rating=4.6
    ),
    TravelOption(
        service="Uber",
        mode="UberGo",
        cost=120,
        eta_minutes=10,
        eta_variance=3,
        rating=4.7
    ),
    TravelOption(
        service="Ola",
        mode="Auto",
        cost=60,
        eta_minutes=12,
        eta_variance=4,
        rating=4.4
    ),
]

# ===============================
# OLA RIDE INTEGRATION
# ===============================

def get_ola_ride_estimates(
    pickup_lat: float, 
    pickup_lon: float,
    drop_lat: float, 
    drop_lon: float
) -> List[TravelOption]:
    """
    Get real ride estimates from Ola
    
    Requires: OLA_API_KEY in .env
    
    Free tier includes:
    - Unlimited location requests
    - Ride estimates
    - Basic tracking
    """
    
    if not OLA_API_KEY or USE_MOCK_SERVICES:
        print("Using mock travel data. To use real Ola API, add OLA_API_KEY to .env")
        return MOCK_OPTIONS
    
    try:
        headers = {
            "Authorization": f"Bearer {OLA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "pickup_latitude": pickup_lat,
            "pickup_longitude": pickup_lon,
            "drop_latitude": drop_lat,
            "drop_longitude": drop_lon
        }
        
        # Get estimates from Ola
        response = requests.post(
            "https://api.olarides.com/v1/rides/estimates",
            headers=headers,
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            rides = response.json().get("rides", [])
            options = []
            
            for ride in rides:
                try:
                    option = TravelOption(
                        service="Ola",
                        mode=ride.get("category", "Ride"),
                        cost=float(ride.get("amount", 0)),
                        eta_minutes=int(ride.get("eta", 0) / 60),  # Convert seconds to minutes
                        eta_variance=1.5,
                        rating=float(ride.get("rating", 4.5) or 4.5)
                    )
                    options.append(option)
                except (ValueError, TypeError):
                    continue
            
            if options:
                return options
        
        print(f"Ola API error: {response.status_code}")
        
    except requests.exceptions.Timeout:
        print("Ola API timeout")
    except requests.exceptions.ConnectionError:
        print("No connection to Ola API")
    except Exception as e:
        print(f"Ola integration error: {e}")
    
    return MOCK_OPTIONS

def book_ola_ride(
    pickup_lat: float,
    pickup_lon: float,
    drop_lat: float,
    drop_lon: float,
    ride_type: str = "Ride",
    user_phone: str = None,
    auto_confirm: bool = True
) -> Dict[str, Any]:
    """
    Book a ride on Ola directly
    
    Prerequisites:
    - User must have Ola account
    - Payment method must be saved
    - API key with booking permissions
    
    Returns: Booking confirmation or error
    """
    
    if not OLA_API_KEY or USE_MOCK_SERVICES:
        return {
            "status": "mock_booking",
            "message": "Using mock booking. Real booking requires OLA_API_KEY and Ola account.",
            "ride_id": "MOCK" + str(datetime.now().timestamp())[-6:],
            "eta": 8,
            "cost": 95
        }
    
    try:
        headers = {
            "Authorization": f"Bearer {OLA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "pickup_latitude": pickup_lat,
            "pickup_longitude": pickup_lon,
            "drop_latitude": drop_lat,
            "drop_longitude": drop_lon,
            "ride_type": ride_type,
            "auto_assign": auto_confirm
        }
        
        if user_phone:
            payload["customer_phone"] = user_phone
        
        response = requests.post(
            "https://api.olarides.com/v1/rides/request",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            booking = response.json()
            return {
                "status": "confirmed",
                "ride_id": booking.get("ride_request_id"),
                "driver": booking.get("driver", {}),
                "eta": booking.get("eta"),
                "cost": booking.get("estimated_fare"),
                "vehicle": booking.get("vehicle", {}),
                "pickup_address": booking.get("pickup_address"),
                "drop_address": booking.get("drop_address")
            }
        
        elif response.status_code == 401:
            raise Exception("Ola API key invalid or expired")
        elif response.status_code == 400:
            error = response.json().get("error", {})
            raise Exception(f"Bad request: {error}")
        else:
            raise Exception(f"Ola API error: {response.status_code}")
        
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Booking request timed out"}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": "Cannot connect to Ola"}
    except Exception as e:
        return {"status": "error", "message": f"Booking failed: {str(e)}"}

# ===============================
# UBER INTEGRATION
# ===============================

def get_uber_ride_estimates(
    pickup_lat: float,
    pickup_lon: float,
    drop_lat: float,
    drop_lon: float
) -> List[TravelOption]:
    """
    Get real ride estimates from Uber
    
    Requires: UBER_API_KEY in .env
    
    Free tier includes:
    - Ride estimates
    - Limited tracking
    """
    
    if not UBER_API_KEY or USE_MOCK_SERVICES:
        return MOCK_OPTIONS
    
    try:
        headers = {
            "Authorization": f"Bearer {UBER_API_KEY}",
            "Accept-Language": "en_IN"
        }
        
        params = {
            "start_latitude": pickup_lat,
            "start_longitude": pickup_lon,
            "end_latitude": drop_lat,
            "end_longitude": drop_lon
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
                try:
                    # Parse price string (e.g., "$5-$10" or "₹200-₹300")
                    estimate = price.get("estimate", "0")
                    
                    # Extract numeric value
                    cost = 0
                    if estimate:
                        # Try to get number
                        import re
                        numbers = re.findall(r'\d+', estimate)
                        if numbers:
                            cost = float(numbers[0])
                    
                    duration_minutes = int(price.get("duration", 0) / 60)
                    
                    if cost > 0:  # Only add if has valid cost
                        option = TravelOption(
                            service="Uber",
                            mode=price.get("display_name", "UberGo"),
                            cost=cost,
                            eta_minutes=duration_minutes,
                            eta_variance=2.0,
                            rating=4.7
                        )
                        options.append(option)
                
                except (ValueError, TypeError):
                    continue
            
            if options:
                return options
        
        print(f"Uber API error: {response.status_code}")
        
    except Exception as e:
        print(f"Uber integration error: {e}")
    
    return MOCK_OPTIONS

def book_uber_ride(
    pickup_lat: float,
    pickup_lon: float,
    drop_lat: float,
    drop_lon: float,
    ride_type: str = "UberGo",
    user_id: str = None
) -> Dict[str, Any]:
    """
    Book a ride on Uber directly
    
    Prerequisites:
    - User OAuth consent obtained
    - Payment method saved on Uber
    - API has ride request capability
    
    Note: Uber requires OAuth 2.0, not just API key
    """
    
    if not UBER_API_KEY or USE_MOCK_SERVICES:
        return {
            "status": "mock_booking",
            "message": "Using mock booking. Real booking requires Uber OAuth setup.",
            "request_id": "MOCK-" + str(datetime.now().timestamp())[-6:],
            "eta": 10,
            "cost": 120
        }
    
    try:
        headers = {
            "Authorization": f"Bearer {UBER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "start_latitude": pickup_lat,
            "start_longitude": pickup_lon,
            "end_latitude": drop_lat,
            "end_longitude": drop_lon,
            "product_id": ride_type
        }
        
        if user_id:
            payload["user_id"] = user_id
        
        response = requests.post(
            "https://api.uber.com/v1.2/requests",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code in [200, 202]:
            request_data = response.json()
            return {
                "status": "confirmed",
                "request_id": request_data.get("request_id"),
                "status_code": request_data.get("status"),
                "driver": request_data.get("driver", {}),
                "eta": request_data.get("eta"),
                "vehicle": request_data.get("vehicle", {}),
                "surge_multiplier": request_data.get("surge_multiplier"),
                "cost_estimate": request_data.get("price", {}).get("display")
            }
        else:
            error = response.json()
            raise Exception(f"Booking failed: {error}")
        
    except Exception as e:
        return {"status": "error", "message": f"Uber booking failed: {str(e)}"}

# ===============================
# UNIFIED INTERFACE
# ===============================

def get_all_travel_options(
    start_lat: float = None,
    start_lon: float = None,
    end_lat: float = None,
    end_lon: float = None
) -> List[TravelOption]:
    """Get all available travel options from Ola and Uber"""
    
    start_lat = start_lat or USER_LATITUDE
    start_lon = start_lon or USER_LONGITUDE
    end_lat = end_lat or 13.1939  # Default to IIT Madras
    end_lon = end_lon or 80.1180
    
    all_options = []
    
    # Get Ola options
    try:
        ola_options = get_ola_ride_estimates(start_lat, start_lon, end_lat, end_lon)
        all_options.extend(ola_options)
    except:
        pass
    
    # Get Uber options
    try:
        uber_options = get_uber_ride_estimates(start_lat, start_lon, end_lat, end_lon)
        all_options.extend(uber_options)
    except:
        pass
    
    # If nothing found, use mock
    if not all_options:
        all_options = MOCK_OPTIONS
    
    # Sort by ETA and limit to 3
    all_options.sort(key=lambda x: x.eta_minutes)
    return all_options[:3]

def get_travel_option(
    start_lat: float = None,
    start_lon: float = None,
    end_lat: float = None,
    end_lon: float = None
) -> TravelOption:
    """Get best travel option"""
    options = get_all_travel_options(start_lat, start_lon, end_lat, end_lon)
    return options[0] if options else MOCK_OPTIONS[0]

def execute_booking(
    service: str,
    ride_type: str,
    pickup_lat: float,
    pickup_lon: float,
    drop_lat: float,
    drop_lon: float,
    user_phone: str = None
) -> Dict[str, Any]:
    """Execute actual ride booking based on service"""
    
    if service.lower() == "ola":
        return book_ola_ride(
            pickup_lat, pickup_lon, drop_lat, drop_lon,
            ride_type, user_phone
        )
    elif service.lower() == "uber":
        return book_uber_ride(
            pickup_lat, pickup_lon, drop_lat, drop_lon,
            ride_type
        )
    else:
        return {"status": "error", "message": f"Unknown service: {service}"}
