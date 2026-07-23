import time
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ExpressionModel:
    """
    The unified target state for all CHITTI actuators at a given point in time.
    Fulfills Engineering Rule #16 (Unified Actuation Rule).
    """
    eyes_state: Dict[str, Any] = field(default_factory=dict)
    head_state: Dict[str, Any] = field(default_factory=dict)
    neck_state: Dict[str, Any] = field(default_factory=dict)
    voice_state: Dict[str, Any] = field(default_factory=dict)
    led_state: Dict[str, Any] = field(default_factory=dict)
    face_state: Dict[str, Any] = field(default_factory=dict)
    body_state: Dict[str, Any] = field(default_factory=dict)
    
    emotion_state: str = "Neutral"
    animation_state: str = "Idle"
    
    priority: int = 0
    cancelable: bool = True
    duration_ms: int = 0
    timestamp: float = field(default_factory=time.time)
