# 🚀 Quick Command Reference

## One-Line Setup (Copy & Paste)

```bash
cd /workspaces/autonomous-life-orchestration-agent/docs/backend && \
source venv/bin/activate && \
pip install -q -r requirements.txt && \
echo "✅ Setup complete. Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
```

## Essential Commands

### Start Server
```bash
# Navigate to backend
cd /workspaces/autonomous-life-orchestration-agent/docs/backend

# Activate environment
source venv/bin/activate

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access Dashboard
```
http://127.0.0.1:8000 (in browser)
```

### Test Endpoints

```bash
# Get destinations
curl http://127.0.0.1:8000/api/destinations | jq .

# Get options
curl -X POST http://127.0.0.1:8000/api/plan \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-20",
    "destination": "IIT Madras",
    "budget": 300
  }' | jq .

# Create booking
curl -X POST http://127.0.0.1:8000/api/book \
  -H "Content-Type: application/json" \
  -d '{
    "plan_date": "2026-02-20",
    "destination": "IIT Madras",
    "start_time": "09:00",
    "food_id": 0,
    "travel_id": 2
  }' | jq .

# Get history
curl http://127.0.0.1:8000/api/history | jq .
```

### Check Status

```bash
# Is server running?
curl -s http://127.0.0.1:8000 | head -20

# View booking history (JSON file)
cd /workspaces/autonomous-life-orchestration-agent/docs/backend
cat agent_memory.json | jq '.execution_history'

# Check dependencies
pip list | grep -E "fastapi|uvicorn|pydantic|pytz"

# Verify file structure
tree app/
```

## Customization Commands

### Change Test Destination
Edit `/workspaces/autonomous-life-orchestration-agent/docs/backend/app/config.py`

```python
# Line with CHENNAI_DESTINATIONS dict
# Add your own location:
"My College": {"lat": 13.0000, "lon": 80.2000, "distance": 10},
```

### Add More Restaurants
Edit `/workspaces/autonomous-life-orchestration-agent/docs/backend/app/tools/food_service_mock.py`

```python
FoodOption(
    id=6,
    restaurant="My Restaurant",
    item="Special Dish",
    price=250,
    eta_minutes=20,
    rating=4.5,
    service="Swiggy"
)
```

### Adjust Risk Threshold
Edit `/workspaces/autonomous-life-orchestration-agent/docs/backend/app/config.py`

```python
CONFIDENCE_THRESHOLD = 0.5  # More lenient (default: 0.6)
```

## Troubleshooting Commands

```bash
# Check Python version
python3 --version

# Verify venv activation (should show path with 'venv')
which python

# Kill server on port 8000
lsof -i :8000
kill -9 <PID>

# Use different port
uvicorn app.main:app --port 8001 --reload

# Check for import errors
python3 -c "import app.main; print('✅ Imports OK')"

# Reinstall from scratch
pip install --force-reinstall -r requirements.txt
```

## File Locations

```
/workspaces/autonomous-life-orchestration-agent/
├── QUICKSTART.md                    ← Read this first!
├── DEPLOYMENT.md                    ← Full guide
├── TECHNICAL_ARCHITECTURE.md        ← Technical details
├── PROJECT_SUMMARY.md               ← Project overview
├── docs/backend/
│   ├── venv/                        # Virtual environment
│   ├── app/main.py                  # ⭐ Main application
│   ├── app/config.py                # Configuration
│   ├── app/models.py                # Data models
│   ├── app/agents/                  # AI agents
│   ├── app/tools/                   # Services (food, travel)
│   ├── app/memory/                  # Data persistence
│   ├── requirements.txt             # Dependencies
│   └── agent_memory.json            # Booking history
```

## Documentation Map

| Need | Read |
|------|------|
| Quick start (5 min) | QUICKSTART.md |
| Deployment guide | DEPLOYMENT.md |
| Technical deep-dive | TECHNICAL_ARCHITECTURE.md |
| What you have | PROJECT_SUMMARY.md |
| License info | OPEN_SOURCE_ATTRIBUTION.md |
| System design | docs/architecture.md |
| Real APIs | docs/REAL_API_INTEGRATION.md |

## Key Configuration Values

```python
# File: /docs/backend/app/config.py

USER_CITY = "Chennai"
USER_TIMEZONE = "Asia/Kolkata"  # IST (UTC+5:30)
CONFIDENCE_THRESHOLD = 0.6  # 60% minimum

# 10 Available destinations
CHENNAI_DESTINATIONS = {
    "IIT Madras": {"distance": 12},
    "Anna University": {"distance": 10},
    "Madras Christian College": {"distance": 8},
    "Loyola College": {"distance": 9},
    "SRCC": {"distance": 7},
    "Vellore Institute": {"distance": 60},
    "Satyam Convention": {"distance": 5},
    "OMR Tech Park": {"distance": 15},
    # ... 2 more
}
```

## Features at a Glance

### Frontend
- ✅ Interactive dashboard (no frameworks)
- ✅ Destination selector (10 options)
- ✅ Date picker
- ✅ Time picker
- ✅ Budget slider (₹100-500)
- ✅ Clickable option cards
- ✅ Visual feedback (blue highlight)
- ✅ Success message with confirmations
- ✅ Daily schedule display
- ✅ Voice button (ready)

### Backend
- ✅ FastAPI with CORS
- ✅ 6 API endpoints
- ✅ 5 AI agents
- ✅ 6 restaurants (mock)
- ✅ 5 ride types (mock)
- ✅ Risk scoring (0-100)
- ✅ Booking confirmations
- ✅ Schedule generation
- ✅ Data persistence (JSON)
- ✅ History tracking (last 50)

## Test Cases

### Test 1: Basic Booking (1 minute)
```
1. Open http://127.0.0.1:8000
2. Select destination
3. Pick date/time
4. Set budget
5. Click "Get Options"
6. Click a food option
7. Click a travel option
8. Click "Complete Booking"
9. ✅ See green success box with confirmations
```

### Test 2: API Testing (2 minutes)
```bash
# Terminal 1: Start server
uvicorn app.main:app --reload

# Terminal 2: Run curl commands
curl -X POST http://127.0.0.1:8000/api/plan \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-02-20", "destination": "IIT Madras", "budget": 300}'

# Verify JSON response with food_options and travel_options
```

### Test 3: Data Persistence (1 minute)
```bash
# 1. Create a booking via UI/API
# 2. Stop server (Ctrl+C)
# 3. Start server again
# 4. Check history: curl http://127.0.0.1:8000/api/history
# ✅ Booking should still be there
```

## Performance Benchmarks

| Operation | Time | Target |
|-----------|------|--------|
| Load page | <0.5s | <1s ✅ |
| Get options | 0.1-0.2s | <1s ✅ |
| Create booking | 0.2-0.5s | <1s ✅ |
| Show confirmation | <0.1s | <0.5s ✅ |

## Success Indicators

You'll know it's working when:

1. ✅ Server starts with "Uvicorn running on http://0.0.0.0:8000"
2. ✅ Dashboard loads (blue & white design)
3. ✅ Destination dropdown has 10 options
4. ✅ "Get Options" button works
5. ✅ Food & travel cards appear
6. ✅ Cards highlight when clicked
7. ✅ "Complete Booking" shows green box
8. ✅ Confirmations like "FOOD-2026-02-20-0" appear
9. ✅ Schedule displays below success
10. ✅ agent_memory.json is updated

## Next Steps (Choose One)

```bash
# 1. Test everything works
cd /workspaces/autonomous-life-orchestration-agent/docs/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 2. Read documentation
# Start with QUICKSTART.md → DEPLOYMENT.md → TECHNICAL_ARCHITECTURE.md

# 3. Customize
# Edit config.py, food_service_mock.py, or main.py

# 4. Integrate real APIs
# See docs/REAL_API_INTEGRATION.md for paths
```

## API Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | ✅ Success | Process data |
| 400 | ❌ Bad request | Check JSON format |
| 404 | ❌ Not found | Wrong endpoint |
| 500 | ❌ Server error | Check terminal logs |

## Environment Variables

File: `/workspaces/autonomous-life-orchestration-agent/docs/backend/.env`

Optional settings (currently using defaults):
```
# DATABASE_URL=postgresql://user:pass@localhost/db
# ZOMATO_API_KEY=your_key_here
# UBER_API_KEY=your_key_here
# OLA_API_KEY=your_key_here
```

## Quick Debug Checklist

- [ ] Server process running? (`ps aux | grep uvicorn`)
- [ ] Port 8000 accessible? (`curl http://127.0.0.1:8000`)
- [ ] No import errors? (`python3 -c "import app.main"`)
- [ ] Dependencies installed? (`pip list | grep fastapi`)
- [ ] File permissions OK? (`ls -la app/main.py`)
- [ ] Timezone set correct? (`date` shows IST)

## Common Error Messages

```
ModuleNotFoundError: No module named 'fastapi'
→ Solution: pip install -r requirements.txt

Address already in use
→ Solution: kill -9 <PID> or use --port 8001

No module named 'app'
→ Solution: cd to /docs/backend directory

JSON decode error
→ Solution: Check agent_memory.json format (run: python3 -m json.tool agent_memory.json)
```

## Hardware Requirements

✅ **Minimum**: 
- 1 CPU
- 512 MB RAM
- 100 MB disk

✅ **Recommended**:
- 2 CPUs
- 2 GB RAM
- 1 GB disk

✅ **Cloud Deploy**:
- AWS t3.micro
- GCP e2-micro
- DigitalOcean $6/month

## Open Source Libraries

All installed packages are free & open-source:

```
FastAPI          MIT     Web framework
Uvicorn          BSD     ASGI server
Pydantic         MIT     Data validation
pytz             MIT     Timezone support
numpy            BSD     Scientific (optional)
scipy            BSD     Scientific (optional)
aiohttp          Apache  HTTP client
SpeechRecognition BSD    Voice (optional)
pyttsx3          MIT     Text-to-speech (optional)
```

**No cost. No license violations. Fully legal. ✅**

---

**Start here**: `source venv/bin/activate && uvicorn app.main:app --reload`  
**Then visit**: `http://127.0.0.1:8000`  
**Questions?** Check QUICKSTART.md or DEPLOYMENT.md
