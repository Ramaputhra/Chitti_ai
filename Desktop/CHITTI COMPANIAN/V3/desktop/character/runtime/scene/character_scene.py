from enum import Enum

class CharacterScene(Enum):
    """
    S36B-R1: Canonical Character Scene Enum.
    Represents high-level runtime scenes INSIDE Character Runtime.
    """
    BOOT = "BOOT"
    WAKE = "WAKE"
    GREETING = "GREETING"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    TALKING = "TALKING"
    WORKING = "WORKING"
    PRESENTING = "PRESENTING"
    SEARCHING = "SEARCHING"
    NAVIGATING = "NAVIGATING"
    REMINDER = "REMINDER"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    IDLE = "IDLE"
    SLEEP = "SLEEP"
    EDGE_DOT = "EDGE_DOT"
    HIDDEN = "HIDDEN"

class ScenePriority(Enum):
    """
    S36B-R1: Scene Priority Hierarchy.
    ERROR > WARNING > REMINDER > PRESENTING > WORKING > TALKING > IDLE
    """
    IDLE = 1
    TALKING = 2
    WORKING = 3
    PRESENTING = 4
    REMINDER = 5
    WARNING = 6
    ERROR = 7
