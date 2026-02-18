from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json

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
from app.models import UserPreferences

app = FastAPI(
    title="Student Morning Routine Planner",
    description="AI-powered scheduling for students",
    version="1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
context_agent = ContextAgent()
planning_agent = PlanningAgent()
risk_agent = RiskAgent()
execution_agent = ExecutionAgent()
schedule_agent = ScheduleAgent()
memory = MemoryStore()


@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    """Serve the dashboard"""
    dashboard_file = Path(__file__).parent / "static" / "index.html"
    if dashboard_file.exists():
        return dashboard_file.read_text()
    return get_default_dashboard()


@app.get("/api/config")
def get_config():
    """Get default configuration"""
    return {
        "city": "Chennai",
        "timezone": "Asia/Kolkata",
        "user_preferences": {
            "class_location": "IIT Madras",
            "class_start_time": "09:00",
            "cuisine_preferences": ["South Indian", "Fast Food"],
            "food_budget": 200
        }
    }


@app.post("/api/preferences")
def save_preferences(prefs: UserPreferences):
    """Save user preferences"""
    memory.save_user_preferences(prefs.dict())
    return {"status": "saved", "preferences": prefs}


@app.get("/api/preferences")
def load_preferences():
    """Load user preferences"""
    prefs = memory.get_user_preferences()
    return prefs if prefs else {
        "location": "Indiranagar, Bangalore",
        "food_budget": 200,
        "class_start_time": "09:00"
    }


@app.get("/api/run")
def run_agent(
    class_time: str = Query("09:00"),
    location: str = Query("IIT Madras")
):
    """Run the complete morning routine planner"""
    try:
        # Gather context
        user_prefs = {
            "class_start_time": class_time,
            "class_location": location
        }
        context = context_agent.gather(user_prefs)
        
        # Create plan
        plan = planning_agent.create_plan(context, user_prefs)
        
        # Get food and travel options
        food_options = get_all_food_options()
        travel_options = get_all_travel_options()
        
        if not food_options or not travel_options:
            return {
                "state": "ERROR",
                "message": "Could not fetch food or travel options",
                "context": context
            }
        
        selected_food = food_options[0]
        selected_travel = travel_options[0]
        
        # Evaluate risk
        risk = risk_agent.evaluate(selected_food, selected_travel, context)
        
        state_name = AgentState.COMPLETED.name
        message = None
        execution = None
        
        # Check confidence threshold
        if risk["confidence"] < CONFIDENCE_THRESHOLD:
            state_name = AgentState.WAITING_FOR_OVERRIDE.name
            message = f"Confidence level {risk['confidence']*100:.0f}% is below threshold. User approval needed."
        else:
            # Execute the plan
            execution = execution_agent.execute(selected_food, selected_travel, user_prefs)
            memory.log_execution({
                "food": selected_food.dict() if hasattr(selected_food, 'dict') else selected_food,
                "travel": selected_travel.dict() if hasattr(selected_travel, 'dict') else selected_travel,
                "confidence": risk["confidence"],
                "buffer": risk["buffer_minutes"]
            })
        
        # Generate schedule
        schedule = schedule_agent.generate(user_prefs)
        
        return {
            "state": state_name,
            "message": message,
            "context": context,
            "plan": plan,
            "food_options": [opt.dict() if hasattr(opt, 'dict') else opt for opt in food_options],
            "travel_options": [opt.dict() if hasattr(opt, 'dict') else opt for opt in travel_options],
            "selected_food": selected_food.dict() if hasattr(selected_food, 'dict') else selected_food,
            "selected_travel": selected_travel.dict() if hasattr(selected_travel, 'dict') else selected_travel,
            "risk": risk,
            "execution": execution,
            "schedule": schedule
        }
    
    except Exception as e:
        return {
            "state": "ERROR",
            "error": str(e),
            "details": "An error occurred while planning your morning routine"
        }


@app.get("/api/history")
def get_history(limit: int = Query(10)):
    """Get execution history"""
    history = memory.get_execution_history(limit)
    return {"history": history, "count": len(history)}


@app.post("/api/approve")
def approve_execution(food_item: str, travel_mode: str):
    """User approves the execution"""
    execution = execution_agent.execute(
        {"item": food_item, "restaurant": "Selected", "service": "User"},
        {"mode": travel_mode, "service": "User", "cost": 0}
    )
    memory.log_execution({
        "food": food_item,
        "travel": travel_mode,
        "approved_by": "user"
    })
    return {"status": "approved", "execution": execution}


def get_default_dashboard() -> str:
    """Return a clean, non-AI-looking dashboard"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Morning Routine Planner</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: #f5f5f5;
            color: #333;
        }
        
        .header {
            background: white;
            padding: 20px;
            border-bottom: 1px solid #eee;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .header h1 { font-size: 22px; font-weight: 600; }
        .header p { font-size: 13px; color: #666; margin-top: 4px; }
        
        .container {
            max-width: 900px;
            margin: 20px auto;
            padding: 0 20px;
        }
        
        .controls {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .control-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .control-group label {
            display: block;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 5px;
            color: #555;
        }
        
        .control-group input {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .actions {
            display: flex;
            gap: 10px;
        }
        
        button {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .btn-primary {
            background: #2c3e50;
            color: white;
        }
        
        .btn-primary:hover { background: #1a252f; }
        
        .btn-secondary {
            background: #ecf0f1;
            color: #333;
        }
        
        .btn-secondary:hover { background: #ddd; }
        
        .results {
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            padding: 20px;
            display: none;
        }
        
        .results.active { display: block; }
        
        .status-banner {
            padding: 12px 16px;
            border-radius: 4px;
            margin-bottom: 20px;
            font-size: 13px;
            font-weight: 500;
        }
        
        .status-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status-warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .status-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        
        .section {
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }
        
        .section:last-child { border-bottom: none; padding-bottom: 0; }
        
        .section-title {
            font-size: 13px;
            font-weight: 600;
            color: #555;
            text-transform: uppercase;
            margin-bottom: 12px;
            letter-spacing: 0.5px;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .info-card {
            padding: 12px;
            background: #f9f9f9;
            border-radius: 4px;
            border-left: 3px solid #2c3e50;
        }
        
        .info-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 4px;
            font-weight: 500;
        }
        
        .info-value {
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }
        
        .options-list {
            display: grid;
            gap: 10px;
        }
        
        .option-item {
            padding: 12px;
            background: #fafafa;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .option-item:hover {
            background: #f0f0f0;
            border-color: #2c3e50;
        }
        
        .option-title {
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .option-detail {
            font-size: 13px;
            color: #666;
        }
        
        .confidence-score {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 8px;
        }
        
        .confidence-high { background: #d4edda; color: #155724; }
        .confidence-medium { background: #fff3cd; color: #856404; }
        .confidence-low { background: #f8d7da; color: #721c24; }
        
        .loading {
            text-align: center;
            padding: 30px;
            display: none;
        }
        
        .loading.active {
            display: block;
        }
        
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f0f0f0;
            border-top: 3px solid #2c3e50;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .error-message {
            padding: 12px;
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Morning Routine Planner</h1>
        <p>Get to class on time with optimal food and travel choices</p>
    </div>
    
    <div class="container">
        <div class="controls">
            <div class="control-group">
                <div>
                    <label>Class Time</label>
                    <input type="time" id="classTime" value="09:00">
                </div>
                <div>
                    <label>Location</label>
                    <input type="text" id="location" value="IIT Madras" placeholder="Your school/college">
                </div>
            </div>
            <div class="actions">
                <button class="btn-primary" onclick="runPlanner()">Plan My Morning</button>
                <button class="btn-secondary" onclick="clearResults()">Clear</button>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 12px; color: #666;">Planning your morning...</p>
        </div>
        
        <div class="results" id="results"></div>
    </div>
    
    <script>
        async function runPlanner() {
            const classTime = document.getElementById('classTime').value;
            const location = document.getElementById('location').value;
            
            if (!classTime || !location) {
                alert('Please fill in all fields');
                return;
            }
            
            document.getElementById('loading').classList.add('active');
            document.getElementById('results').innerHTML = '';
            document.getElementById('results').classList.remove('active');
            
            try {
                const response = await fetch(`/api/run?class_time=${classTime}&location=${encodeURIComponent(location)}`);
                const data = await response.json();
                
                displayResults(data);
            } catch (error) {
                showError('Failed to fetch plan: ' + error.message);
            } finally {
                document.getElementById('loading').classList.remove('active');
            }
        }
        
        function displayResults(data) {
            const resultsDiv = document.getElementById('results');
            let html = '';
            
            if (data.state === 'ERROR') {
                html += `<div class="error-message">${data.details || data.error}</div>`;
            } else {
                // Status banner
                const isApprovalNeeded = data.state === 'WAITING_FOR_OVERRIDE';
                const statusClass = isApprovalNeeded ? 'status-warning' : 'status-success';
                const statusText = isApprovalNeeded ? 'Needs Your Approval' : 'Ready to Execute';
                html += `<div class="status-banner ${statusClass}">${statusText}</div>`;
                
                // Context
                if (data.context) {
                    html += `
                        <div class="section">
                            <div class="section-title">Current Status</div>
                            <div class="info-grid">
                                <div class="info-card">
                                    <div class="info-label">Time</div>
                                    <div class="info-value">${data.context.current_time}</div>
                                </div>
                                <div class="info-card">
                                    <div class="info-label">Class In</div>
                                    <div class="info-value">${data.context.minutes_until_class} minutes</div>
                                </div>
                                <div class="info-card">
                                    <div class="info-label">Distance</div>
                                    <div class="info-value">${data.context.distance_km.toFixed(1)} km</div>
                                </div>
                            </div>
                        </div>
                    `;
                }
                
                // Food Options
                if (data.food_options && data.food_options.length > 0) {
                    html += `<div class="section">
                        <div class="section-title">Food Options</div>
                        <div class="options-list">`;
                    
                    data.food_options.forEach(food => {
                        const selected = data.selected_food && data.selected_food.restaurant === food.restaurant ? 'selected' : '';
                        html += `
                            <div class="option-item ${selected}">
                                <div class="option-title">${food.item} - ${food.restaurant}</div>
                                <div class="option-detail">₹${food.price} | ${food.eta_minutes} mins | ${food.service}</div>
                                <div class="option-detail">Rating: ${food.rating}</div>
                            </div>
                        `;
                    });
                    
                    html += `</div></div>`;
                }
                
                // Travel Options
                if (data.travel_options && data.travel_options.length > 0) {
                    html += `<div class="section">
                        <div class="section-title">Travel Options</div>
                        <div class="options-list">`;
                    
                    data.travel_options.forEach(travel => {
                        const selected = data.selected_travel && data.selected_travel.service === travel.service && data.selected_travel.mode === travel.mode ? 'selected' : '';
                        html += `
                            <div class="option-item ${selected}">
                                <div class="option-title">${travel.service} ${travel.mode}</div>
                                <div class="option-detail">₹${travel.cost.toFixed(0)} | ${travel.eta_minutes} mins | Rating: ${travel.rating}</div>
                            </div>
                        `;
                    });
                    
                    html += `</div></div>`;
                }
                
                // Risk Assessment
                if (data.risk) {
                    const confidence = data.risk.confidence;
                    const percentage = (confidence * 100).toFixed(0);
                    const confidenceClass = confidence >= 0.8 ? 'confidence-high' : confidence >= 0.6 ? 'confidence-medium' : 'confidence-low';
                    
                    html += `
                        <div class="section">
                            <div class="section-title">Risk Assessment</div>
                            <div class="info-grid">
                                <div class="info-card">
                                    <div class="info-label">Confidence</div>
                                    <div class="info-value">${percentage}%</div>
                                    <div class="confidence-score ${confidenceClass}">
                                        ${confidence >= 0.8 ? 'Safe' : confidence >= 0.6 ? 'Moderate' : 'Risky'}
                                    </div>
                                </div>
                                <div class="info-card">
                                    <div class="info-label">Time Buffer</div>
                                    <div class="info-value">${data.risk.buffer_minutes} min</div>
                                </div>
                            </div>
                            ${data.message ? `<div class="error-message" style="margin-top: 10px;">${data.message}</div>` : ''}
                        </div>
                    `;
                }
                
                // Schedule
                if (data.schedule && data.schedule.length > 0) {
                    html += `
                        <div class="section">
                            <div class="section-title">Today's Schedule</div>
                            <div class="options-list">`;
                    
                    data.schedule.forEach(item => {
                        html += `<div class="option-item" style="cursor: default;"><div class="option-detail">${item}</div></div>`;
                    });
                    
                    html += `</div></div>`;
                }
            }
            
            resultsDiv.innerHTML = html;
            resultsDiv.classList.add('active');
        }
        
        function showError(message) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = `<div class="error-message">${message}</div>`;
            resultsDiv.classList.add('active');
        }
        
        function clearResults() {
            document.getElementById('results').classList.remove('active');
        }
        
        // Run on page load
        window.addEventListener('load', () => {
            document.getElementById('classTime').value = '09:00';
            document.getElementById('location').value = 'IIT Madras';
        });
    </script>
</body>
</html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
