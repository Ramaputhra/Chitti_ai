from enum import Enum

class VisualPriority(Enum):
    CRITICAL = 1000
    ERROR = 900
    WARNING = 800
    ACTIVE_CONVERSATION = 700
    PRESENTATION = 600
    MEDIA = 500
    PRODUCTIVITY = 400
    BACKGROUND = 300
    IDLE = 100

class PriorityEngine:
    """
    S36E: Priority Engine governing visual competition and yielding.
    Lower priority visuals automatically yield to higher priority visuals.
    """
    @staticmethod
    def get_priority_weight(priority: VisualPriority) -> int:
        return priority.value

    @staticmethod
    def should_yield(current: VisualPriority, incoming: VisualPriority) -> bool:
        return incoming.value > current.value
