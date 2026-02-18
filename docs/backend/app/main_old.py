from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.state_machine import AgentState
from app.agents.content_agent import ContextAgent
from app.agents.planning_agent import PlanningAgent
from app.agents.risk_agent import RiskAgent
from app.agents.execution_agent import ExecutionAgent
from app.agents.schedule_agent import ScheduleAgent
from app.memory.store import MemoryStore
from app.tools.food_service_mock import get_food_option
from app.tools.travel_service_mock import get_travel_option

app = FastAPI(title="Autonomous Life Orchestration Agent")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    """Serve the web dashboard"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Autonomous Life Orchestration Agent</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                max-width: 1000px;
                width: 100%;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 { font-size: 28px; margin-bottom: 10px; }
            .header p { opacity: 0.9; font-size: 14px; }
            .content {
                padding: 40px;
            }
            .button-group {
                display: flex;
                gap: 15px;
                margin-bottom: 30px;
                flex-wrap: wrap;
            }
            button {
                padding: 12px 30px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .btn-run {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .btn-run:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4); }
            .btn-clear {
                background: #f0f0f0;
                color: #333;
            }
            .btn-clear:hover { background: #e0e0e0; }
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
                color: #667eea;
                font-weight: 600;
            }
            .loading::after {
                content: '';
                display: inline-block;
                width: 10px;
                height: 10px;
                background: #667eea;
                border-radius: 50%;
                margin-left: 8px;
                animation: blink 1s infinite;
            }
            @keyframes blink {
                0%, 50% { opacity: 1; }
                100% { opacity: 0.3; }
            }
            .output {
                background: #f5f5f5;
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
                display: none;
            }
            .output.show { display: block; }
            .output h2 {
                color: #333;
                margin-bottom: 15px;
                font-size: 18px;
            }
            .state-badge {
                display: inline-block;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 600;
                margin-right: 15px;
                margin-bottom: 15px;
            }
            .state-completed { background: #d4edda; color: #155724; }
            .state-waiting { background: #fff3cd; color: #856404; }
            .state-executing { background: #cce5ff; color: #004085; }
            .section {
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
            }
            .section h3 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 16px;
            }
            .metric {
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #f0f0f0;
            }
            .metric:last-child { border-bottom: none; }
            .metric-label { color: #666; font-weight: 500; }
            .metric-value { color: #333; font-weight: 600; }
            .confidence-bar {
                width: 100%;
                height: 8px;
                background: #ddd;
                border-radius: 4px;
                overflow: hidden;
                margin-top: 5px;
            }
            .confidence-fill {
                height: 100%;
                background: linear-gradient(90deg, #ff6b6b, #ffd43b, #51cf66);
                transition: width 0.3s ease;
            }
            .list {
                list-style: none;
                padding: 0;
            }
            .list li {
                padding: 8px 0;
                border-bottom: 1px solid #f0f0f0;
            }
            .list li:last-child { border-bottom: none; }
            .list li::before {
                content: '✓ ';
                color: #51cf66;
                font-weight: bold;
                margin-right: 8px;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #f5c6cb;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Autonomous Life Orchestration Agent</h1>
                <p>Confidence-based autonomous decision making for morning routines</p>
            </div>
            <div class="content">
                <div class="button-group">
                    <button class="btn-run" onclick="runAgent()">Run Agent</button>
                    <button class="btn-clear" onclick="clearOutput()">Clear</button>
                </div>
                <div class="loading" id="loading">Running agent...</div>
                <div class="output" id="output"></div>
            </div>
        </div>

        <script>
            async function runAgent() {
                const loading = document.getElementById('loading');
                const output = document.getElementById('output');
                
                loading.style.display = 'block';
                output.classList.remove('show');
                
                try {
                    console.log('Fetching /run endpoint...');
                    const response = await fetch('/run');
                    console.log('Response status:', response.status);
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    console.log('Data received:', data);
                    displayResult(data);
                } catch (error) {
                    console.error('Error:', error);
                    output.innerHTML = `<div class="error"><strong>Error:</strong> ${error.message}</div>`;
                    output.classList.add('show');
                } finally {
                    loading.style.display = 'none';
                }
            }

            function displayResult(data) {
                const output = document.getElementById('output');
                const state = data.state || 'UNKNOWN';
                const stateClass = state === 'COMPLETED' ? 'state-completed' : 
                                   state === 'WAITING_FOR_OVERRIDE' ? 'state-waiting' : 
                                   'state-executing';
                
                let html = `<h2>Execution Result</h2>`;
                html += `<div class="state-badge ${stateClass}">${state}</div>`;
                
                if (data.message) {
                    html += `<p style="color: #666; margin-bottom: 20px;">${data.message}</p>`;
                }

                // Context
                if (data.context) {
                    html += `<div class="section">
                        <h3>📍 Context</h3>
                        <div class="metric">
                            <span class="metric-label">Current Time</span>
                            <span class="metric-value">${data.context.current_time}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Minutes Until Class</span>
                            <span class="metric-value">${data.context.minutes_until_class} min</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Distance</span>
                            <span class="metric-value">${data.context.distance_km} km</span>
                        </div>
                    </div>`;
                }

                // Plan
                if (data.plan) {
                    html += `<div class="section">
                        <h3>📋 Plan</h3>
                        <ul class="list">`;
                    data.plan.forEach(item => {
                        html += `<li>${item}</li>`;
                    });
                    html += `</ul></div>`;
                }

                // Risk & Confidence
                if (data.risk) {
                    const confidence = data.risk.confidence;
                    const percentage = (confidence * 100).toFixed(0);
                    html += `<div class="section">
                        <h3>⚠️ Risk Evaluation</h3>
                        <div class="metric">
                            <span class="metric-label">Confidence Score</span>
                            <span class="metric-value">${percentage}%</span>
                        </div>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: ${percentage}%"></div>
                        </div>
                        <div class="metric" style="margin-top: 15px;">
                            <span class="metric-label">Buffer Time</span>
                            <span class="metric-value">${data.risk.buffer_minutes} minutes</span>
                        </div>
                    </div>`;
                }

                // Execution
                if (data.execution) {
                    html += `<div class="section">
                        <h3>✅ Execution</h3>
                        <div class="metric">
                            <span class="metric-label">Food Ordered</span>
                            <span class="metric-value">${data.execution.food_ordered}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Travel Booked</span>
                            <span class="metric-value">${data.execution.travel_booked}</span>
                        </div>
                    </div>`;
                }

                // Schedule
                if (data.schedule) {
                    html += `<div class="section">
                        <h3>📅 Daily Schedule</h3>
                        <ul class="list">`;
                    data.schedule.forEach(item => {
                        html += `<li>${item}</li>`;
                    });
                    html += `</ul></div>`;
                }

                output.innerHTML = html;
                output.classList.add('show');
            }

            function clearOutput() {
                document.getElementById('output').classList.remove('show');
                document.getElementById('loading').style.display = 'none';
            }

            // Make sure functions are available globally
            window.runAgent = runAgent;
            window.clearOutput = clearOutput;

            // Auto-run on page load
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', runAgent);
            } else {
                runAgent();
            }
        </script>
    </body>
    </html>
    """


@app.get("/run")
def run_agent():
    state = AgentState.PLANNING

    memory = MemoryStore()

    context = ContextAgent().gather()
    plan = PlanningAgent().create_plan(context)

    food = get_food_option()
    travel = get_travel_option()

    risk = RiskAgent().evaluate(food, travel, context)

    if risk["confidence"] < 0.6:
        state = AgentState.WAITING_FOR_OVERRIDE
        return {
            "state": state.name,
            "message": "Confidence too low. User approval required.",
            "risk": risk
        }

    state = AgentState.EXECUTING
    execution = ExecutionAgent().execute(food, travel)
    schedule = ScheduleAgent().generate()

    memory.log_execution({
        "execution": execution,
        "confidence": risk["confidence"]
    })

    state = AgentState.COMPLETED

    return {
        "state": state.name,
        "context": context,
        "plan": plan,
        "risk": risk,
        "execution": execution,
        "schedule": schedule
    }
