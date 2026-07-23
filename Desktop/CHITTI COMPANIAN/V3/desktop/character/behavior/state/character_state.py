from enum import Enum, auto

class CharacterState(Enum):
    """
    S34B: Canonical Character State Enum.
    """
    BOOT = "BOOT"
    WAKE = "WAKE"
    GREETING = "GREETING"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    TALKING = "TALKING"
    WORKING = "WORKING"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    SLEEP = "SLEEP"
    EDGE_DOT = "EDGE_DOT"

class CharacterPriority(Enum):
    """
    S34B: Character Priority Hierarchy.
    ERROR > WARNING > WAKE > TALKING > WORKING > IDLE
    """
    IDLE = 1
    WORKING = 2
    TALKING = 3
    WAKE = 4
    WARNING = 5
    ERROR = 6
