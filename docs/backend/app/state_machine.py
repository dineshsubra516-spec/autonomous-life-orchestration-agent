from enum import Enum, auto


class AgentState(Enum):
    SLEEPING = auto()
    PLANNING = auto()
    RISK_EVALUATION = auto()
    WAITING_FOR_OVERRIDE = auto()
    EXECUTING = auto()
    COMPLETED = auto()
