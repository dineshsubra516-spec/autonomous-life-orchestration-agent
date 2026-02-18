# Autonomous Life Orchestration Agent

A functional AI-powered student morning routine planner that makes autonomous decisions about food delivery and transportation with confidence-based approval.

## Features

**For Students in India:**
- Integrated with Swiggy/Zomato for food delivery
- Integrated with Ola/Uber for ride-sharing
- IST (Indian Standard Time) timezone support
- Chennai-specific defaults (customizable to any city)
- Student-friendly budget constraints

**Core Capabilities:**
- Autonomous decision-making with confidence scoring
- Risk assessment (travel time buffer, delivery delays, cost)
- User approval workflow for low-confidence scenarios
- Execution history and performance tracking
- Daily schedule generation
- User preferences management

## How It Works

### Morning Routine Planning Flow

1. **Context Gathering** - Collects current time, class schedule, location, and distance
2. **Planning** - Creates actionable plan for food and travel
3. **Food Discovery** - Fetches restaurants from Swiggy/Zomato within budget & time
4. **Travel Options** - Gets ride estimates from Ola/Uber
5. **Risk Evaluation** - Calculates confidence score based on:
   - Time buffer until class
   - Delivery/travel time estimates and variance
   - Cost constraints
6. **Decision**:
   - If confidence > 60%: Execute automatically
   - If confidence < 60%: Request user approval
7. **Schedule Generation** - Creates daily schedule with classes and activities

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip or pip3

### Quick Start

```bash
cd docs/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment (optional - for real APIs)
cp .env.example .env
# Edit .env with your API keys

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000` in your browser.

### Configuration

Edit `docs/backend/.env` to configure:

```
# API Keys (leave blank to use mock data)
ZOMATO_API_KEY=your_key_here
SWIGGY_API_KEY=your_key_here
UBER_API_KEY=your_key_here
OLA_API_KEY=your_key_here

# User Location
USER_CITY=Chennai
USER_LATITUDE=13.0827
USER_LONGITUDE=80.2707
USER_TIMEZONE=Asia/Kolkata

# Thresholds
CONFIDENCE_THRESHOLD=0.6
MAX_FOOD_ETA=30
MAX_TRAVEL_ETA=20
MIN_BUFFER_TIME=15
```

## API Endpoints

### Web Interface
- `GET /` - Main dashboard

### REST API
- `GET /api/run` - Run the planner
  - Query params: `class_time` (HH:MM), `location`
  - Returns: Full plan with options and confidence score
  
- `GET /api/preferences` - Get user preferences
- `POST /api/preferences` - Save user preferences
- `GET /api/history` - Get execution history
- `POST /api/approve` - User approval for low-confidence decisions

## Data Models

### FoodOption
```
restaurant: str
item: str
price: float (in INR)
eta_minutes: int
eta_variance: float
rating: float
service: str (Swiggy/Zomato)
```

### TravelOption
```
service: str (Ola/Uber)
mode: str (Ride/Auto/XL)
cost: float (in INR)
eta_minutes: int
eta_variance: float
rating: float
```

### Risk Assessment
```
confidence: float (0.0 to 1.0)
buffer_minutes: int
reasoning: dict
recommendation: str
```

## Project Structure

```
docs/backend/
├── app/
│   ├── main.py              # FastAPI server & dashboard
│   ├── config.py            # Configuration & settings
│   ├── models.py            # Data models
│   ├── state_machine.py     # Agent states
│   ├── agents/              # Agent implementations
│   │   ├── content_agent.py      # Context perception
│   │   ├── planning_agent.py     # Plan generation
│   │   ├── risk_agent.py         # Risk evaluation
│   │   ├── execution_agent.py    # Booking execution
│   │   └── schedule_agent.py     # Schedule generation
│   ├── tools/               # External service integrations
│   │   ├── food_service_mock.py    # Swiggy/Zomato integration
│   │   └── travel_service_mock.py  # Ola/Uber integration
│   └── memory/
│       └── store.py         # Persistence layer
├── requirements.txt
├── .env
└── agent_memory.json        # Execution history

scripts/
└── simulate_morning.py      # Demo script
```

## Current Status

Fully functional with:
- Mock services for Swiggy, Zomato, Ola, Uber (no API key required)
- Complete confidence-based decision system
- User preferences management
- Execution history tracking
- Clean, non-AI web interface

Mock data includes:
- Sangeetha Veg (Swiggy) - South Indian
- MTR (Zomato) - Dosa
- Kaldan Continental (Swiggy) - Continental
- Ola/Uber with various ride types

## Example Response

```json
{
  "state": "COMPLETED",
  "context": {
    "current_time": "08:45",
    "minutes_until_class": 30,
    "distance_km": 8.5,
    "class_location": "IIT Madras"
  },
  "food_options": [...],
  "travel_options": [...],
  "risk": {
    "confidence": 0.95,
    "buffer_minutes": 5,
    "recommendation": "Safe to execute"
  },
  "execution": {
    "food_ordered": "Idli + Dosa Combo from Sangeetha Veg",
    "travel_booked": "Ola Ride",
    "status": "Confirmed"
  },
  "schedule": [...]
}
```

## For Real API Integration

To use real APIs:

1. Get API keys from:
   - Zomato: https://developers.zomato.com/
   - Swiggy: Contact Swiggy enterprise
   - Ola: https://olacabs.com/developer
   - Uber: https://developer.uber.com/

2. Add keys to `.env` file

3. Update `config.py` USE_MOCK_SERVICES = false

The system will automatically fall back to mock services if real APIs fail or are not configured.

## Testing

```bash
# Test API directly
curl http://127.0.0.1:8000/api/run?class_time=09:00&location=IIT%20Madras

# Test with jq (formatted)
curl -s http://127.0.0.1:8000/api/run | python -m json.tool
```

## Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Time**: pytz (timezone handling)
- **Data**: Pydantic (validation), JSON (persistence)
- **HTTP**: requests, aiohttp
- **Frontend**: Vanilla JavaScript, CSS Grid

## Architecture Principles

1. **Confidence-First**: High confidence triggers autonomous execution
2. **Transparent**: Every decision is logged with reasoning
3. **Fallback**: Mock services ensure development works offline
4. **Modular**: Agents are independent and testable
5. **Privacy**: No data is sent to third parties except chosen services

## License

MIT - See LICENSE file

---

## Customization for Your Context

Edit `docs/backend/app/config.py` to customize for your location:

```python
USER_CITY = "Your City"
USER_LATITUDE = 13.0827  # Your home latitude
USER_LONGITUDE = 80.2707  # Your home longitude
USER_TIMEZONE = "Asia/Kolkata"
```

Update `FoodOption` and `TravelOption` mocks in `tools/*.py` for your local restaurants and services.


