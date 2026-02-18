from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import pytz
import math

from app.state_machine import AgentState
from app.agents.content_agent import ContextAgent
from app.agents.planning_agent import PlanningAgent
from app.agents.risk_agent import RiskAgent
from app.agents.execution_agent import ExecutionAgent
from app.agents.schedule_agent import ScheduleAgent
from app.memory.store import MemoryStore
from app.tools.food_service_mock import get_all_food_options
from app.tools.travel_service_mock import get_all_travel_options
from app.config import CONFIDENCE_THRESHOLD

app = FastAPI(
    title="Daily Routine Planner",
    description="AI-powered autonomous planning for students",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chennai locations with coordinates
CHENNAI_DESTINATIONS = {
    "IIT Madras": {"lat": 12.9914, "lon": 80.2303, "distance": 12},
    "Anna University": {"lat": 13.0179, "lon": 80.2254, "distance": 10},
    "Madras Christian College": {"lat": 13.0033, "lon": 80.1995, "distance": 8},
    "Loyola College": {"lat": 13.0042, "lon": 80.2591, "distance": 9},
    "SRCC": {"lat": 13.0523, "lon": 80.2456, "distance": 7},
    "Vellore Institute": {"lat": 12.9667, "lon": 79.1333, "distance": 60},
    "Satyam Convention": {"lat": 13.0827, "lon": 80.2707, "distance": 5},
    "OMR Tech Park": {"lat": 12.8397, "lon": 80.2318, "distance": 15},
}

# Agents
context_agent = ContextAgent()
planning_agent = PlanningAgent()
risk_agent = RiskAgent()
execution_agent = ExecutionAgent()
schedule_agent = ScheduleAgent()
memory = MemoryStore()

# Track selections
selected_selections = {}

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    return get_dashboard_html()

@app.get("/api/destinations")
def get_destinations():
    """Get available destinations in Chennai"""
    return {
        "destinations": list(CHENNAI_DESTINATIONS.keys()),
        "details": CHENNAI_DESTINATIONS
    }

@app.get("/api/food-options")
def get_food_options_api(budget: int = Query(200)):
    """Get available food options"""
    options = get_all_food_options(budget)
    return {
        "options": [
            {
                "id": i,
                "restaurant": opt.restaurant,
                "item": opt.item,
                "price": opt.price,
                "eta_minutes": opt.eta_minutes,
                "eta_variance": opt.eta_variance,
                "rating": opt.rating,
                "service": opt.service
            } for i, opt in enumerate(options)
        ],
        "count": len(options)
    }

@app.get("/api/travel-options")
def get_travel_options_api():
    """Get available travel options"""
    options = get_all_travel_options()
    return {
        "options": [
            {
                "id": i,
                "service": opt.service,
                "mode": opt.mode,
                "cost": opt.cost,
                "eta_minutes": opt.eta_minutes,
                "eta_variance": opt.eta_variance,
                "rating": opt.rating
            } for i, opt in enumerate(options)
        ],
        "count": len(options)
    }

@app.post("/api/plan")
def plan_day(
    plan_date: str = Query("2026-02-18"),
    destination: str = Query("IIT Madras"),
    start_time: str = Query("09:00"),
    budget: int = Query(200)
):
    """Plan the day with selections"""
    try:
        # Parse input
        tz = pytz.timezone("Asia/Kolkata")
        plan_datetime = tz.localize(datetime.strptime(f"{plan_date} {start_time}", "%Y-%m-%d %H:%M"))
        
        if destination not in CHENNAI_DESTINATIONS:
            raise ValueError(f"Invalid destination: {destination}")
        
        # Gather context with error handling
        user_prefs = {
            "class_start_time": start_time,
            "class_location": destination,
            "distance_km": CHENNAI_DESTINATIONS[destination]["distance"]
        }
        
        try:
            context = context_agent.gather(user_prefs)
        except Exception as ctx_err:
            print(f"Context error: {ctx_err}")
            context = {
                "current_time": datetime.now(tz).strftime("%H:%M"),
                "timezone": "Asia/Kolkata",
                "date": datetime.now(tz).strftime("%A, %B %d, %Y"),
                "minutes_until_class": 60,
                "distance_km": CHENNAI_DESTINATIONS[destination]["distance"],
                "class_location": destination,
                "weather": "Sunny"
            }
        
        context["plan_date"] = plan_date
        context["destination"] = destination
        
        # Get options
        food_options = get_all_food_options(budget)
        travel_options = get_all_travel_options()
        
        if not food_options or not travel_options:
            return {
                "state": "ERROR",
                "error": "Could not fetch options",
                "context": {
                    "current_time": context.get("current_time"),
                    "plan_date": plan_date,
                    "destination": destination,
                    "distance_km": CHENNAI_DESTINATIONS[destination]["distance"],
                    "minutes_until": context.get("minutes_until_class", 60)
                }
            }
        
        # Create plan with error handling
        try:
            plan = planning_agent.create_plan(context, user_prefs)
        except Exception as plan_err:
            print(f"Planning error: {plan_err}")
            plan = []
        
        # Return with all options for user selection
        return {
            "state": "SELECTION",
            "context": {
                "current_time": context.get("current_time", "00:00"),
                "plan_date": plan_date,
                "destination": destination,
                "distance_km": CHENNAI_DESTINATIONS[destination]["distance"],
                "minutes_until": max(0, context.get("minutes_until_class", 60))
            },
            "plan": plan if plan else [],
            "food_options": [
                {
                    "id": i,
                    "restaurant": opt.restaurant,
                    "item": opt.item,
                    "price": opt.price,
                    "eta_minutes": opt.eta_minutes,
                    "rating": opt.rating,
                    "service": opt.service
                } for i, opt in enumerate(food_options)
            ],
            "travel_options": [
                {
                    "id": i,
                    "service": opt.service,
                    "mode": opt.mode,
                    "cost": opt.cost,
                    "eta_minutes": opt.eta_minutes,
                    "rating": opt.rating
                } for i, opt in enumerate(travel_options)
            ]
        }
    
    except Exception as e:
        print(f"Plan day error: {e}")
        # Return error with some basic context
        return {
            "state": "ERROR",
            "error": str(e),
            "context": {
                "current_time": "00:00",
                "plan_date": plan_date,
                "destination": destination,
                "distance_km": 10,
                "minutes_until": 60
            }
        }

@app.post("/api/book")
def book_selections(
    plan_date: str = Query("2026-02-18"),
    destination: str = Query("IIT Madras"),
    start_time: str = Query("09:00"),
    food_id: int = Query(0),
    travel_id: int = Query(0)
):
    """Book selected food and travel"""
    try:
        # Get options again
        food_options = get_all_food_options(300)
        travel_options = get_all_travel_options()
        
        if food_id >= len(food_options) or travel_id >= len(travel_options):
            return {
                "state": "ERROR",
                "error": "Invalid selection"
            }
        
        selected_food = food_options[food_id]
        selected_travel = travel_options[travel_id]
        
        # Get context for risk evaluation
        user_prefs = {
            "class_start_time": start_time,
            "class_location": destination,
            "distance_km": CHENNAI_DESTINATIONS[destination]["distance"]
        }
        
        context = context_agent.gather(user_prefs)
        
        # Evaluate risk
        risk = risk_agent.evaluate(selected_food, selected_travel, context)
        
        # Execute booking
        execution = execution_agent.execute(selected_food, selected_travel, user_prefs)
        
        # Generate schedule
        schedule = schedule_agent.generate(user_prefs)
        
        # Log to memory
        memory.log_execution({
            "date": plan_date,
            "destination": destination,
            "food": selected_food.restaurant,
            "travel": selected_travel.service,
            "confidence": risk["confidence"],
            "status": "booked"
        })
        
        return {
            "state": "SUCCESS",
            "booking": {
                "food": {
                    "restaurant": selected_food.restaurant,
                    "item": selected_food.item,
                    "price": selected_food.price,
                    "eta_minutes": selected_food.eta_minutes,
                    "service": selected_food.service,
                    "confirmation": f"FOOD-{plan_date}-{food_id}"
                },
                "travel": {
                    "service": selected_travel.service,
                    "mode": selected_travel.mode,
                    "cost": selected_travel.cost,
                    "eta_minutes": selected_travel.eta_minutes,
                    "confirmation": f"RIDE-{plan_date}-{travel_id}"
                },
                "risk_confidence": int(risk["confidence"] * 100),
                "buffer_minutes": risk["buffer_minutes"]
            },
            "schedule": schedule
        }
    
    except Exception as e:
        return {
            "state": "ERROR",
            "error": str(e)
        }

@app.get("/api/history")
def get_history(limit: int = Query(5)):
    """Get recent bookings"""
    history = memory.get_execution_history(limit)
    return {
        "history": history,
        "count": len(history)
    }

def get_dashboard_html() -> str:
    """Generate interactive dashboard HTML"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Study Planner - Daily Routine</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800;900&family=Space+Mono:wght@400;700&family=Tangerine:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            font-family: 'Times New Roman', Times, serif;
            background: linear-gradient(180deg, #ffffff 0%, #f5f7fa 50%, #eef2f9 100%);
            color: #1a202c;
            line-height: 1.6;
            position: relative;
            overflow-x: hidden;
            min-height: 100vh;
        }

        /* Background doodles - Large and visible */
        .doodle-bg {
            position: fixed;
            z-index: -1;
            opacity: 0.08;
            pointer-events: none;
        }

        .doodle-top-left {
            top: -50px;
            left: -50px;
            width: 400px;
            height: 400px;
        }

        .doodle-bottom-right {
            bottom: -100px;
            right: -50px;
            width: 450px;
            height: 450px;
        }

        .header {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafb 100%);
            border-bottom: 2px solid #e8eef7;
            padding: 64px 24px 48px;
            text-align: center;
            position: relative;
            z-index: 10;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        .header h1 {
            font-family: 'Poppins', sans-serif;
            font-size: 48px;
            font-weight: 900;
            margin-bottom: 16px;
            color: #0f172a;
            letter-spacing: -1.5px;
            background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .header p {
            font-family: 'Tangerine', cursive;
            font-size: 28px;
            color: #64748b;
            font-weight: 700;
            letter-spacing: 0.3px;
        }

        .container {
            max-width: 1100px;
            margin: 0 auto;
            padding: 48px 24px;
            position: relative;
            z-index: 5;
        }

        .section {
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 36px;
            border: 2px solid #e8eef7;
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .section::before {
            content: '';
            position: absolute;
            top: -40%;
            right: -10%;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(59, 130, 246, 0.08) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
        }

        .section:hover {
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.12);
            transform: translateY(-4px);
            border-color: #d0d9eb;
        }

        .section-title {
            font-family: 'Tangerine', cursive;
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 28px;
            color: #0f172a;
            display: flex;
            align-items: center;
            gap: 14px;
            position: relative;
            z-index: 2;
        }

        .section-title::before {
            content: '';
            display: inline-block;
            width: 5px;
            height: 28px;
            background: linear-gradient(180deg, #3b82f6 0%, #7c3aed 100%);
            border-radius: 3px;
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 24px;
            margin-bottom: 28px;
            position: relative;
            z-index: 2;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        .form-group label {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            margin-bottom: 10px;
            color: #334155;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1.2px;
        }

        .form-group input,
        .form-group select {
            font-family: 'Inter', sans-serif;
            padding: 14px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 15px;
            transition: all 0.25s;
            background: #f8fafc;
            color: #1a202c;
            font-weight: 500;
        }

        .form-group input::placeholder {
            color: #94a3b8;
        }

        .form-group input:hover,
        .form-group select:hover {
            border-color: #cbd5e1;
            background: white;
        }

        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #3b82f6;
            background: white;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
        }

        .button-group {
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
            position: relative;
            z-index: 2;
        }

        button {
            font-family: 'Poppins', sans-serif;
            padding: 14px 28px;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            letter-spacing: 0.5px;
        }

        .btn-primary {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            flex: 1;
            min-width: 150px;
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
        }

        .btn-primary:hover {
            box-shadow: 0 10px 28px rgba(59, 130, 246, 0.45);
            transform: translateY(-3px);
        }

        .btn-primary:active {
            transform: translateY(-1px);
        }

        .btn-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .btn-secondary {
            background: #f1f5f9;
            color: #334155;
            min-width: 110px;
            border: 2px solid #e2e8f0;
            font-weight: 600;
        }

        .btn-secondary:hover {
            background: #e2e8f0;
            border-color: #cbd5e1;
            transform: translateY(-2px);
        }

        .options-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 24px;
            margin: 28px 0;
            position: relative;
            z-index: 2;
        }

        .option-card {
            border: 2px solid #e8eef7;
            border-radius: 14px;
            padding: 24px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            background: linear-gradient(135deg, #ffffff 0%, #f8fafb 100%);
            position: relative;
            overflow: hidden;
        }

        .option-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent);
            transition: left 0.6s ease;
            pointer-events: none;
        }

        .option-card:hover::before {
            left: 100%;
        }

        .option-card:hover {
            border-color: #3b82f6;
            box-shadow: 0 10px 28px rgba(59, 130, 246, 0.2);
            transform: translateY(-6px);
        }

        .option-card.selected {
            border-color: #3b82f6;
            background: linear-gradient(135deg, #eff6ff 0%, #f0f4f8 100%);
            box-shadow: 0 10px 28px rgba(59, 130, 246, 0.3);
        }

        .option-card.selected::after {
            content: '';
            position: absolute;
            top: 14px;
            right: 14px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            font-weight: bold;
            font-size: 18px;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }

        .option-name {
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            font-size: 17px;
            margin-bottom: 10px;
            color: #0f172a;
        }

        .option-detail {
            font-family: 'Times New Roman', Times, serif;
            font-size: 14px;
            color: #64748b;
            margin-bottom: 8px;
            font-weight: 500;
        }

        .option-price {
            font-family: 'Poppins', sans-serif;
            font-size: 18px;
            font-weight: 800;
            color: #10b981;
            margin-top: 14px;
        }

        .option-rating {
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            color: #f59e0b;
            margin-top: 10px;
            font-weight: 600;
        }

        .success-message {
            background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
            color: #065f46;
            padding: 24px;
            border-radius: 14px;
            margin: 28px 0;
            border: 2px solid #d1fae5;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
        }

        .success-title {
            font-family: 'Tangerine', cursive;
            font-weight: 700;
            font-size: 24px;
            margin-bottom: 14px;
        }

        .success-detail {
            font-family: 'Times New Roman', Times, serif;
            font-size: 15px;
            margin-bottom: 10px;
            color: #047857;
            font-weight: 500;
        }

        .confirmation-code {
            font-family: 'Space Mono', monospace;
            background: white;
            padding: 12px 14px;
            border-radius: 8px;
            margin-top: 10px;
            font-size: 13px;
            color: #334155;
            border: 1px solid #cbd5e1;
            word-break: break-all;
            font-weight: 500;
        }

        .risk-indicator {
            padding: 24px;
            border-radius: 12px;
            margin: 18px 0;
            border: 2px solid;
        }

        .risk-safe {
            background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
            color: #065f46;
            border-color: #d1fae5;
        }

        .risk-warning {
            background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
            color: #92400e;
            border-color: #fde68a;
        }

        .schedule-list {
            list-style: none;
            position: relative;
            z-index: 2;
        }

        .schedule-item {
            font-family: 'Inter', sans-serif;
            padding: 18px;
            background: linear-gradient(135deg, #f8fafc 0%, #f0f4f8 100%);
            border-radius: 10px;
            margin-bottom: 14px;
            border-left: 5px solid #3b82f6;
            transition: all 0.25s;
            font-weight: 500;
        }

        .schedule-item:hover {
            background: linear-gradient(135deg, #f1f5f9 0%, #e8f0f8 100%);
            transform: translateX(6px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
        }

        .schedule-time {
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            color: #3b82f6;
            font-size: 13px;
        }

        .spinner {
            border: 3px solid #f1f5f9;
            border-top: 3px solid #3b82f6;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 36px;
            }

            .form-grid {
                grid-template-columns: 1fr;
            }

            .options-grid {
                grid-template-columns: 1fr;
            }

            .section {
                padding: 28px;
            }

            .button-group {
                flex-direction: column;
            }

            .btn-primary,
            .btn-secondary {
                width: 100%;
            }

            .doodle-bg {
                display: none;
            }
        }
    </style>
</head>
<body>
    <!-- Doodle Background SVGs -->
    <svg class="doodle-bg doodle-top-left" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
        <!-- Notebook Stack -->
        <rect x="30" y="40" width="100" height="130" fill="none" stroke="#3b82f6" stroke-width="2.5" rx="6"/>
        <line x1="40" y1="65" x2="120" y2="65" stroke="#3b82f6" stroke-width="1.5" opacity="0.7"/>
        <line x1="40" y1="85" x2="120" y2="85" stroke="#3b82f6" stroke-width="1.5" opacity="0.7"/>
        <line x1="40" y1="105" x2="120" y2="105" stroke="#3b82f6" stroke-width="1.5" opacity="0.7"/>
        <line x1="40" y1="125" x2="120" y2="125" stroke="#3b82f6" stroke-width="1.5" opacity="0.7"/>
        
        <!-- Pencil -->
        <line x1="200" y1="30" x2="200" y2="140" stroke="#f59e0b" stroke-width="9" stroke-linecap="round"/>
        <polygon points="200,140 192,158 208,158" fill="#ec4899"/>
        
        <!-- Eraser -->
        <rect x="195" y="140" width="10" height="20" fill="#ff6b6b" rx="1"/>
        
        <!-- Pen -->
        <rect x="270" y="50" width="9" height="100" fill="none" stroke="#10b981" stroke-width="2.5" rx="4"/>
        <circle cx="274.5" cy="45" r="6" fill="none" stroke="#10b981" stroke-width="2.5"/>
        <rect x="268" y="150" width="13" height="12" fill="none" stroke="#10b981" stroke-width="2.5" rx="2"/>
        
        <!-- Ruler -->
        <rect x="160" y="190" width="120" height="12" fill="none" stroke="#06b6d4" stroke-width="2" rx="2"/>
        <line x1="170" y1="185" x2="170" y2="207" stroke="#06b6d4" stroke-width="1.5"/>
        <line x1="190" y1="185" x2="190" y2="207" stroke="#06b6d4" stroke-width="1.5"/>
        <line x1="210" y1="185" x2="210" y2="207" stroke="#06b6d4" stroke-width="1.5"/>
        <line x1="230" y1="185" x2="230" y2="207" stroke="#06b6d4" stroke-width="1.5"/>
        <line x1="250" y1="185" x2="250" y2="207" stroke="#06b6d4" stroke-width="1.5"/>
        <line x1="270" y1="185" x2="270" y2="207" stroke="#06b6d4" stroke-width="1.5"/>
        
        <!-- Lightbulb - Ideas -->
        <circle cx="90" cy="280" r="18" fill="none" stroke="#fbbf24" stroke-width="2.5"/>
        <path d="M 80 298 Q 75 310 75 320 L 105 320 Q 105 310 100 298" fill="none" stroke="#fbbf24" stroke-width="2.5"/>
        <rect x="90" y="320" width="8" height="14" fill="none" stroke="#fbbf24" stroke-width="2.5" rx="2"/>
        
        <!-- Graduation Cap -->
        <rect x="280" y="250" width="80" height="8" fill="none" stroke="#7c3aed" stroke-width="2.5" rx="2"/>
        <polygon points="310,250 290,220 330,220" fill="none" stroke="#7c3aed" stroke-width="2.5"/>
        <line x1="310" y1="220" x2="310" y2="240" stroke="#7c3aed" stroke-width="2.5"/>
        
        <!-- Check Mark -->
        <path d="M 50 360 L 80 385 L 130 330" fill="none" stroke="#10b981" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>

    <svg class="doodle-bg doodle-bottom-right" viewBox="0 0 450 450" xmlns="http://www.w3.org/2000/svg">
        <!-- Globe -->
        <circle cx="60" cy="60" r="35" fill="none" stroke="#06b6d4" stroke-width="2.5"/>
        <path d="M 25 60 Q 60 80 95 60" fill="none" stroke="#06b6d4" stroke-width="1.5" opacity="0.6"/>
        <path d="M 25 60 Q 60 40 95 60" fill="none" stroke="#06b6d4" stroke-width="1.5" opacity="0.6"/>
        <line x1="60" y1="25" x2="60" y2="95" stroke="#06b6d4" stroke-width="1.5" opacity="0.6"/>
        
        <!-- Laptop -->
        <rect x="140" y="100" width="180" height="120" fill="none" stroke="#7c3aed" stroke-width="2.5" rx="10"/>
        <line x1="150" y1="140" x2="310" y2="140" stroke="#7c3aed" stroke-width="1.5" opacity="0.6"/>
        <line x1="150" y1="170" x2="310" y2="170" stroke="#7c3aed" stroke-width="1.5" opacity="0.6"/>
        <line x1="150" y1="200" x2="310" y2="200" stroke="#7c3aed" stroke-width="1.5" opacity="0.6"/>
        <line x1="110" y1="240" x2="370" y2="240" stroke="#7c3aed" stroke-width="3" opacity="0.5"/>
        
        <!-- Books on Shelves -->
        <rect x="50" y="280" width="23" height="80" fill="none" stroke="#3b82f6" stroke-width="2.5" rx="2"/>
        <rect x="80" y="290" width="23" height="70" fill="none" stroke="#3b82f6" stroke-width="2.5" rx="2"/>
        <rect x="110" y="285" width="23" height="75" fill="none" stroke="#3b82f6" stroke-width="2.5" rx="2"/>
        <rect x="140" y="295" width="23" height="65" fill="none" stroke="#3b82f6" stroke-width="2.5" rx="2"/>
        <rect x="170" y="288" width="23" height="72" fill="none" stroke="#3b82f6" stroke-width="2.5" rx="2"/>
        
        <!-- Calendar/Schedule -->
        <rect x="270" y="280" width="100" height="100" fill="none" stroke="#06b6d4" stroke-width="2.5" rx="6"/>
        <line x1="280" y1="305" x2="360" y2="305" stroke="#06b6d4" stroke-width="2" opacity="0.7"/>
        <line x1="280" y1="330" x2="360" y2="330" stroke="#06b6d4" stroke-width="1.5" opacity="0.5"/>
        <line x1="280" y1="350" x2="360" y2="350" stroke="#06b6d4" stroke-width="1.5" opacity="0.5"/>
        <line x1="280" y1="370" x2="360" y2="370" stroke="#06b6d4" stroke-width="1.5" opacity="0.5"/>
        
        <!-- Desk Elements -->
        <circle cx="300" cy="80" r="8" fill="none" stroke="#f59e0b" stroke-width="2.5" opacity="0.6"/>
        <circle cx="320" cy="95" r="6" fill="none" stroke="#f59e0b" stroke-width="2.5" opacity="0.6"/>
        
        <!-- Brain/Thinking -->
        <circle cx="360" cy="120" r="20" fill="none" stroke="#ec4899" stroke-width="2.5" opacity="0.7"/>
        <path d="M 350 110 Q 345 105 350 100" fill="none" stroke="#ec4899" stroke-width="1.5" opacity="0.6"/>
    </svg>
        <line x1="220" y1="265" x2="300" y2="265" stroke="#06b6d4" stroke-width="2" opacity="0.7"/>
        <line x1="220" y1="290" x2="300" y2="290" stroke="#06b6d4" stroke-width="1.5" opacity="0.5"/>
        <line x1="220" y1="310" x2="300" y2="310" stroke="#06b6d4" stroke-width="1.5" opacity="0.5"/>
        <line x1="220" y1="330" x2="300" y2="330" stroke="#06b6d4" stroke-width="1.5" opacity="0.5"/>
        
        <!-- Study Desk Elements -->
        <circle cx="80" cy="70" r="8" fill="none" stroke="#f59e0b" stroke-width="2.5" opacity="0.6"/>
        <circle cx="100" cy="85" r="6" fill="none" stroke="#f59e0b" stroke-width="2.5" opacity="0.6"/>
    </svg>

    <div class="header">
        <h1>Day Planner</h1>
        <p>Intelligent scheduling for your academic success</p>
    </div>

    <div class="container">
        <!-- Planning Form -->
        <div class="section">
            <div class="section-title">Configure Your Schedule</div>
            
            <div class="form-grid">
                <div class="form-group">
                    <label for="planDate">Date</label>
                    <input type="date" id="planDate">
                </div>
                <div class="form-group">
                    <label for="destination">Destination</label>
                    <select id="destination">
                        <option value="">Select location...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="startTime">Start Time</label>
                    <input type="time" id="startTime" value="09:00">
                </div>
                <div class="form-group">
                    <label for="budget">Budget (Rs)</label>
                    <input type="number" id="budget" value="200" min="100" max="500">
                </div>
            </div>

            <div class="button-group">
                <button class="btn-primary" id="planBtn">Generate Plan</button>
                <button class="btn-secondary" id="clearBtn">Clear</button>
            </div>
        </div>

        <!-- Results Section -->
        <div id="resultsSection" style="display: none;">
            <!-- Risk Assessment -->
            <div class="section" id="riskSection" style="display: none;">
                <div class="section-title">Assessment</div>
                <div id="riskContent"></div>
            </div>

            <!-- Food Selection -->
            <div class="section" id="foodSection" style="display: none;">
                <div class="section-title">Meal Selection</div>
                <div id="foodOptions" class="options-grid"></div>
            </div>

            <!-- Travel Selection -->
            <div class="section" id="travelSection" style="display: none;">
                <div class="section-title">Transportation</div>
                <div id="travelOptions" class="options-grid"></div>
            </div>

            <!-- Booking Button -->
            <div class="section" id="bookingSection" style="display: none;">
                <button class="btn-primary" id="bookBtn" style="width: 100%; padding: 18px 28px; font-size: 17px;">Confirm Booking</button>
            </div>

            <!-- Success Message -->
            <div id="successMessage" style="display: none;">
                <div class="success-message">
                    <div class="success-title">Schedule Confirmed</div>
                    <div id="successContent"></div>
                </div>
            </div>

            <!-- Schedule -->
            <div class="section" id="scheduleSection" style="display: none;">
                <div class="section-title">Daily Schedule</div>
                <ul class="schedule-list" id="scheduleList"></ul>
            </div>
        </div>
    </div>

    <script>
        // State management
        let state = {
            date: null,
            destination: null,
            time: null,
            budget: 200,
            selectedFood: null,
            selectedTravel: null,
            planData: null
        };

        // DOM elements
        const planBtn = document.getElementById('planBtn');
        const clearBtn = document.getElementById('clearBtn');
        const bookBtn = document.getElementById('bookBtn');
        const planDate = document.getElementById('planDate');
        const destination = document.getElementById('destination');
        const startTime = document.getElementById('startTime');
        const budget = document.getElementById('budget');
        const resultsSection = document.getElementById('resultsSection');

        // Initialize
        window.addEventListener('load', () => {
            planDate.valueAsDate = new Date();
            loadDestinations();
        });

        // Load destinations
        async function loadDestinations() {
            try {
                const response = await fetch('/api/destinations');
                const data = await response.json();
                
                destination.innerHTML = '<option value="">Select location...</option>';
                data.destinations.forEach(dest => {
                    const option = document.createElement('option');
                    option.value = dest;
                    const distance = data.details[dest].distance;
                    option.textContent = `${dest} (${distance}km)`;
                    destination.appendChild(option);
                });
                
                destination.value = 'IIT Madras';
            } catch (error) {
                console.error('Error loading destinations:', error);
            }
        }

        // Plan day
        planBtn.addEventListener('click', async () => {
            const date = planDate.value;
            const dest = destination.value;
            const time = startTime.value;
            const bud = parseInt(budget.value);

            if (!date || !dest || !time) {
                alert('Please fill all fields');
                return;
            }

            state = { date, destination: dest, time, budget: bud, selectedFood: null, selectedTravel: null };

            planBtn.disabled = true;
            planBtn.textContent = 'Planning...';

            try {
                const response = await fetch(
                    `/api/plan?plan_date=${date}&destination=${encodeURIComponent(dest)}&start_time=${time}&budget=${bud}`,
                    { method: 'POST' }
                );
                const data = await response.json();

                if (data.state === 'ERROR') {
                    alert('Error: ' + data.error);
                    return;
                }

                state.planData = data;
                console.log('Plan data received:', data);
                displayPlan(data);
                resultsSection.style.display = 'block';
                resultsSection.scrollIntoView({ behavior: 'smooth' });
            } catch (error) {
                console.error('Error planning day:', error);
                alert('Error planning day: ' + error.message);
            } finally {
                planBtn.disabled = false;
                planBtn.textContent = 'Generate Plan';
            }
        });

        // Display plan
        function displayPlan(data) {
            // Validate data structure
            if (!data || !data.context) {
                console.error('Invalid data structure:', data);
                alert('Invalid response from server. Please check browser console.');
                return;
            }

            // Risk
            const riskSection = document.getElementById('riskSection');
            const riskContent = document.getElementById('riskContent');
            riskSection.style.display = 'block';

            const minutesUntil = data.context.minutes_until || 60;
            const riskClass = minutesUntil > 15 ? 'risk-safe' : 'risk-warning';
            riskContent.innerHTML = `
                <div class="${riskClass}">
                    <div style="margin-bottom: 8px;">
                        Time until event: <strong>${minutesUntil}</strong> minutes
                    </div>
                </div>
            `;

            // Food options
            const foodSection = document.getElementById('foodSection');
            const foodOptions = document.getElementById('foodOptions');
            foodSection.style.display = 'block';
            foodOptions.innerHTML = '';

            if (data.food_options && Array.isArray(data.food_options)) {
                data.food_options.forEach(food => {
                    const card = document.createElement('div');
                    card.className = 'option-card';
                    card.innerHTML = `
                        <div class="option-name">${food.item || 'Food Item'}</div>
                        <div class="option-detail">${food.restaurant || 'Restaurant'}</div>
                        <div class="option-detail">Rs ${food.price || 0} | ${food.eta_minutes || 0} min</div>
                        <div class="option-rating">Rating: ${food.rating || 4.5}/5 (${food.service || 'Delivery'})</div>
                        <div class="option-price">Rs ${food.price || 0}</div>
                    `;
                    card.addEventListener('click', () => selectFood(food.id, card));
                    foodOptions.appendChild(card);
                });
            } else {
                foodOptions.innerHTML = '<p>No food options available</p>';
            }

            // Travel options
            const travelSection = document.getElementById('travelSection');
            const travelOptions = document.getElementById('travelOptions');
            travelSection.style.display = 'block';
            travelOptions.innerHTML = '';

            if (data.travel_options && Array.isArray(data.travel_options)) {
                data.travel_options.forEach(travel => {
                    const card = document.createElement('div');
                    card.className = 'option-card';
                    card.innerHTML = `
                        <div class="option-name">${travel.service || 'Service'} ${travel.mode || 'Ride'}</div>
                        <div class="option-detail">Rs ${Math.round(travel.cost || 0)} | ${travel.eta_minutes || 0} min</div>
                        <div class="option-rating">Rating: ${travel.rating || 4.5}/5</div>
                        <div class="option-price">Rs ${Math.round(travel.cost || 0)}</div>
                    `;
                    card.addEventListener('click', () => selectTravel(travel.id, card));
                    travelOptions.appendChild(card);
                });
            } else {
                travelOptions.innerHTML = '<p>No travel options available</p>';
            }

            // Show booking button
            const bookingSection = document.getElementById('bookingSection');
            bookingSection.style.display = 'block';
        }

        // Select food
        function selectFood(id, element) {
            document.querySelectorAll('#foodOptions .option-card').forEach(card => {
                card.classList.remove('selected');
            });
            element.classList.add('selected');
            state.selectedFood = id;
        }

        // Select travel
        function selectTravel(id, element) {
            document.querySelectorAll('#travelOptions .option-card').forEach(card => {
                card.classList.remove('selected');
            });
            element.classList.add('selected');
            state.selectedTravel = id;
        }

        // Book
        bookBtn.addEventListener('click', async () => {
            if (state.selectedFood === null || state.selectedTravel === null) {
                alert('Please select both food and travel options');
                return;
            }

            bookBtn.disabled = true;
            bookBtn.textContent = 'Processing...';

            try {
                const response = await fetch(
                    `/api/book?plan_date=${state.date}&destination=${encodeURIComponent(state.destination)}&start_time=${state.time}&food_id=${state.selectedFood}&travel_id=${state.selectedTravel}`,
                    { method: 'POST' }
                );
                const data = await response.json();

                if (data.state === 'SUCCESS') {
                    showSuccess(data);
                } else {
                    alert('Booking failed: ' + data.error);
                }
            } catch (error) {
                alert('Error booking: ' + error.message);
            } finally {
                bookBtn.disabled = false;
                bookBtn.textContent = 'Confirm Booking';
            }
        });

        // Show success
        function showSuccess(data) {
            document.getElementById('foodSection').style.display = 'none';
            document.getElementById('travelSection').style.display = 'none';
            document.getElementById('bookingSection').style.display = 'none';

            const successMsg = document.getElementById('successMessage');
            const successContent = document.getElementById('successContent');

            const booking = data.booking;
            successContent.innerHTML = `
                <div class="success-detail">
                    <strong>Food Order:</strong> ${booking.food.item} from ${booking.food.restaurant}
                </div>
                <div class="confirmation-code">Confirmation: ${booking.food.confirmation}</div>
                
                <div class="success-detail" style="margin-top: 12px;">
                    <strong>Travel:</strong> ${booking.travel.service} ${booking.travel.mode}
                </div>
                <div class="confirmation-code">Confirmation: ${booking.travel.confirmation}</div>
                
                <div class="success-detail" style="margin-top: 12px;">
                    <strong>Confidence:</strong> ${booking.risk_confidence}%
                </div>
            `;

            successMsg.style.display = 'block';

            // Show schedule
            const scheduleSection = document.getElementById('scheduleSection');
            const scheduleList = document.getElementById('scheduleList');
            scheduleList.innerHTML = '';

            data.schedule.forEach(item => {
                const li = document.createElement('li');
                li.className = 'schedule-item';
                li.textContent = item;
                scheduleList.appendChild(li);
            });

            scheduleSection.style.display = 'block';
            successMsg.scrollIntoView({ behavior: 'smooth' });
        }

        // Clear button
        clearBtn.addEventListener('click', () => {
            // Reset all form fields
            planDate.valueAsDate = new Date();
            destination.value = 'IIT Madras';
            startTime.value = '09:00';
            budget.value = '200';
            
            // Reset state
            state = {
                date: null,
                destination: null,
                time: null,
                budget: 200,
                selectedFood: null,
                selectedTravel: null,
                planData: null
            };
            
            // Hide results section
            resultsSection.style.display = 'none';
            
            // Reset button text
            planBtn.disabled = false;
            planBtn.textContent = 'Generate Plan';
            bookBtn.disabled = false;
            bookBtn.textContent = 'Confirm Booking';
        });
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
