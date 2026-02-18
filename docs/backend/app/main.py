from fastapi import FastAPI

from app.state_machine import AgentState
from app.agents.context_agent import ContextAgent
from app.agents.planning_agent import PlanningAgent
from app.agents.risk_agent import RiskAgent
from app.agents.execution_agent import ExecutionAgent
from app.agents.schedule_agent import ScheduleAgent
from app.memory.store import MemoryStore
from app.tools.food_service_mock import get_food_option
from app.tools.travel_service_mock import get_travel_option

app = FastAPI(title="Autonomous Life Orchestration Agent")


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
