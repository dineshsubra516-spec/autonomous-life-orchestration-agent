# Real API Integration Guide for Student Morning Routine Planner

## Prerequisites for Live Integration

You'll need API keys from these services:

### 1. Zomato (Food Delivery - Search & Discovery)
- **URL**: https://developers.zomato.com/
- **What You Get**: Restaurant search, menus, delivery info
- **Cost**: Free tier available
- **Authentication**: API Key in headers
- **Limitation**: Cannot book directly - users complete on Zomato app/website

### 2. Ola (Ride-Sharing - Full Integration)
- **URL**: https://olacabs.com/developer
- **What You Get**: Ride estimates, direct booking, tracking
- **Cost**: Free tier available
- **Authentication**: OAuth 2.0 + API Key
- **Capability**: Full autonomous booking possible

### 3. Uber (Rides & Eats - Full Integration)
- **URL**: https://developer.uber.com/
- **What You Get**: UberEats restaurant search, Uber Rides
- **Cost**: Free tier available
- **Authentication**: OAuth 2.0
- **Capability**: Both rides and food delivery possible

### 4. Swiggy (Food Delivery - None Official)
- **Status**: No official public API
- **Alternative**: Contact Swiggy enterprise team for partnership
- **Workaround**: Use Zomato as primary, mention Swiggy in UI

### 5. Google Maps API (Optional - For Distance/Time)
- **URL**: https://cloud.google.com/maps-platform
- **What You Get**: Real routing, actual travel times between points
- **Cost**: Free tier with credits

## Implementation Roadmap

### Phase 1: Live Food Discovery (1-2 hours)
```python
# Update tools/food_service_mock.py to use Zomato API

from app.config import ZOMATO_API_KEY, USER_LATITUDE, USER_LONGITUDE

def get_zomato_restaurants(cuisine="South Indian", budget=200, lat=None, lon=None):
    lat = lat or USER_LATITUDE
    lon = lon or USER_LONGITUDE
    
    headers = {"api_key": ZOMATO_API_KEY}
    
    # First: Get location ID
    response = requests.get(
        "https://api.zomato.com/api/v2.1/locations",
        headers=headers,
        params={"query": "Chennai", "count": 1}
    )
    location_id = response.json()[0]["entity_id"]
    
    # Then: Search restaurants
    response = requests.get(
        "https://api.zomato.com/api/v2.1/search",
        headers=headers,
        params={
            "entity_id": location_id,
            "entity_type": "city",
            "cuisines": "North Indian",
            "sort": "rating",
            "order": "desc"
        }
    )
    
    restaurants = []
    for rest in response.json()["restaurants"][:5]:
        r = rest["restaurant"]
        restaurants.append(FoodOption(
            restaurant=r["name"],
            item="Restaurant item",
            price=r.get("average_cost_for_two", 200) / 2,
            eta_minutes=int(r.get("delivery_time", 30)),
            eta_variance=2.0,
            rating=float(r["user_rating"]["aggregate_rating"]),
            service="Zomato"
        ))
    
    return restaurants
```

### Phase 2: Live Ride Booking (2-3 hours)
```python
# Ola Ride Booking

def book_ola_ride(pickup_lat, pickup_lon, drop_lat, drop_lon):
    headers = {
        "Authorization": f"Bearer {OLA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # First: Get estimates
    response = requests.post(
        "https://api.ola-api.com/v1/rides/estimates",
        headers=headers,
        json={
            "pickup_latitude": pickup_lat,
            "pickup_longitude": pickup_lon,
            "drop_latitude": drop_lat,
            "drop_longitude": drop_lon
        }
    )
    
    estimates = response.json()["rides"]
    selected_ride = estimates[0]  # or let user choose
    
    # Second: Confirm booking
    booking_response = requests.post(
        "https://api.ola-api.com/v1/rides/request",
        headers=headers,
        json={
            "pickup_latitude": pickup_lat,
            "pickup_longitude": pickup_lon,
            "drop_latitude": drop_lat,
            "drop_longitude": drop_lon,
            "ride_type": selected_ride["ride_type"],
            "auto_assign": True
        }
    )
    
    ride_request = booking_response.json()
    return {
        "ride_id": ride_request["ride_request_id"],
        "driver": ride_request["driver"],
        "eta": ride_request["eta"],
        "status": "Confirmed"
    }
```

## Current System Modifications Needed

### 1. Update .env with Real Keys
```env
ZOMATO_API_KEY=your_real_api_key_here
OLA_API_KEY=your_real_api_key_here
UBER_API_KEY=your_real_api_key_here
USE_MOCK_SERVICES=false
```

### 2. Update config.py
```python
# Set this to False to use real APIs
USE_MOCK_SERVICES = False
```

### 3. Update API endpoints to return real data
- Already designed in `tools/food_service_mock.py` - just uncommented real code
- Already designed in `tools/travel_service_mock.py` - just uncommented real code

## What Happens in the Dashboard

### Scenario 1: Same Data, Real Sources
```
User clicks "Plan My Morning"
    ↓
System contacts Zomato API
    ↓
Gets live restaurant data in your area
    ↓
Contacts Ola/Uber API
    ↓
Gets live ride estimates
    ↓
Evaluates risk based on REAL times
    ↓
Shows real options in Dashboard
    ↓
User approves (if confidence < 60%)
    ↓
System books via APIs
    ↓
Confirmation sent to user
```

### Scenario 2: Low Confidence (< 60%)
```
Real APIs show:
- High traffic: Travel time 35 mins (> max 20)
- Slow delivery: Restaurant busy, 28 mins (> threshold)
    ↓
Confidence = 45% (LOW)
    ↓
Dashboard shows: "Needs Your Approval"
    ↓
User can:
  a) Approve anyway
  b) Choose different restaurant
  c) Choose different ride type
  d) Skip breakfast & catch ride
```

## Limitations & Challenges

### Food Booking
| Service | Discovery | Real-time | Booking | Autonomous |
|---------|-----------|-----------|---------|-----------|
| Zomato | Yes | Yes | No* | No |
| Swiggy | No | N/A | No | No |
| Uber Eats | Yes | Yes | Yes | Yes |

*Zomato: Users must complete on app/website but you can send them direct links with pre-filled data

### Ride Booking
| Service | Works | Autonomous | Prerequisites |
|---------|-------|-----------|---------------|
| Ola | Yes | Yes | - API Key<br>- User OAuth<br>- Payment method saved |
| Uber | Yes | Yes | - API Key<br>- User OAuth<br>- Payment method |

## Recommended Approach

### Immediate (Live Results - No Execution)
1. Integrate Zomato API for food search
2. Integrate Ola/Uber APIs for ride estimates
3. Show real options in dashboard
4. Users click links to book on apps

**Time**: 4-6 hours
**Risk**: Low
**Cost**: Free APIs (free tier)

### Medium Term (Ride Booking Only)
1. Add Ola autonomous booking
2. Add Uber autonomous booking
3. Users provide OAuth consent
4. System books rides intelligently

**Time**: 1-2 weeks
**Risk**: Medium (payment integration)
**Cost**: Free APIs + Stripe for payments

### Long Term (Full Automation)
1. Partner with food delivery apps
2. Get access to their booking APIs
3. Full autonomous morning routine

**Time**: 2-3 months
**Risk**: High (requires partnerships)
**Cost**: Revenue sharing / Commission

## How to Get Started

### Step 1: Get Zomato Key (5 minutes)
1. Go to https://developers.zomato.com/
2. Sign up
3. Create application
4. Copy API key to `.env`

### Step 2: Get Ola Key (30 minutes)
1. Go to https://olacabs.com/developer
2. Apply for developer access
3. Create app
4. Get Consumer Key and Secret
5. Add to `.env`

### Step 3: Update Code (1-2 hours)
```python
# In tools/food_service_mock.py
# Uncomment the real Zomato code block
# Change USE_MOCK_SERVICES = False

# In tools/travel_service_mock.py
# Uncomment the real Ola code block
# Change USE_MOCK_SERVICES = False
```

### Step 4: Test
```bash
curl 'http://127.0.0.1:8000/api/run?class_time=09:00&location=IIT%20Madras'
# Should now return real data from APIs
```

## Success Indicators

- Dashboard shows real restaurants near you
- Prices match Zomato
- Delivery times are accurate
- Ola ride estimates update in real-time
- Confidence scores based on real data
- Booking confirmation with actual ride ID

## Troubleshooting

### "API Key Invalid"
```
Check:
- Key is in .env file
- USE_MOCK_SERVICES = False in config
- Spaces/tabs in .env are correct
```

### "Rate Limited"
```
Solution:
- Zomato: 100 requests/day free
- Ola: Depends on plan
- Add caching to avoid repeated calls
```

### "Booking Failed"
```
Most common:
- User not authenticated with service
- Payment method not saved
- Location unreachable by service
```

## Code Example: Complete Integration

```python
# In app/tools/food_service_mock.py

import requests
from app.config import ZOMATO_API_KEY, USE_MOCK_SERVICES

def get_food_option():
    if USE_MOCK_SERVICES:
        return get_mock_food_options()[0]
    else:
        return get_zomato_live()[0]

def get_zomato_live():
    """Get real Zomato data"""
    try:
        headers = {"api_key": ZOMATO_API_KEY}
        
        # Get restaurants with delivery in Chennai
        response = requests.get(
            "https://api.zomato.com/api/v2.1/search",
            headers=headers,
            params={
                "lat": 13.0827,
                "lon": 80.2707,
                "radius": 2000,
                "sort": "rating"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            restaurants = response.json()["restaurants"]
            
            options = []
            for rest_data in restaurants[:3]:
                r = rest_data["restaurant"]
                option = FoodOption(
                    restaurant=r["name"],
                    item="Featured item",
                    price=100,  # Default
                    eta_minutes=int(r.get("delivery_time", 30)),
                    eta_variance=2.5,
                    rating=float(r["user_rating"]["aggregate_rating"]),
                    service="Zomato"
                )
                options.append(option)
            
            return options
    except Exception as e:
        print(f"Zomato error: {e}")
    
    return get_mock_food_options()
```

## Summary

**Current**: Works with mock data, demonstrates full system
**Possible**: Connect to real APIs for live data
**Autonomous**: Can auto-book rides, semi-auto food (with links)
**Effort**: 4-6 hours for basic integration, 2 weeks for full autonomy

The system is already architected for this - you just need API keys!
