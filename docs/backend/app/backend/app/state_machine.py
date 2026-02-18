from enum import Enum

class AgentState(Enum):
    SLEEPING = "sleeping"
    PLANNING = "planning"
    RISK_EVALUATION = "risk_evaluation"
    WAITING_FOR_OVERRIDE = "waiting_for_override"
    EXECUTING = "executing"
    COMPLETED = "completed"
