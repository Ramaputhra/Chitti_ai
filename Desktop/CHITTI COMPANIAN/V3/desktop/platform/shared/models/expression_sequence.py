import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

from desktop.platform.shared.models.expression_model import ExpressionModel
from desktop.platform.shared.models.robot_command import RobotCommand


class ExpressionState(Enum):
    """The lifecycle of a scheduled behavior."""
    IDLE = "IDLE"
    QUEUED = "QUEUED"
    PREPARING = "PREPARING"
    PLAYING = "PLAYING"
    INTERRUPTED = "INTERRUPTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class ExpressionSequence:
    """
    The timeline-based container tracking the behavior lifecycle.
    Crucial for debugging, replayability, and deterministic provider execution (Rule 17).
    """
    sequence_id: str
    command: RobotCommand
    
    # Timeline maps millisecond offsets to their target ExpressionModels
    timeline: Dict[int, ExpressionModel] = field(default_factory=dict)
    
    start_time_ms: int = 0
    end_time_ms: int = 0
    state: ExpressionState = ExpressionState.QUEUED
    
    interruptions: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    replay_metadata: Dict[str, Any] = field(default_factory=dict)
