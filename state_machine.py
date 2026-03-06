from enum import Enum
from datetime import datetime


class State(Enum):
    IDLE = "IDLE"
    POLICY_RECEIVED = "POLICY_RECEIVED"
    PARSING_POLICY = "PARSING_POLICY"
    VALIDATING = "VALIDATING"
    REPORT_GENERATED = "REPORT_GENERATED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class StateMachine:
    def __init__(self):
        self.current_state = State.IDLE
        self.history = []

    def transition(self, event: str, next_state: State):
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "from": self.current_state.value,
            "event": event,
            "to": next_state.value
        }
        self.history.append(record)
        self.current_state = next_state

    def get_history(self):
        return self.history