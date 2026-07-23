from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from desktop.platform.shared.models.world_model import WorldState
from desktop.platform.shared.models.activity import ActivitySession
from desktop.platform.shared.models.goal import Project, Goal

@dataclass
class ActiveGoalContext:
    current_project: Optional[Project] = None
    current_goal: Optional[Goal] = None
    recent_goal: Optional[Goal] = None

@dataclass
class RecentActivityBuffer:
    active_activity: Optional[ActivitySession] = None
    previous_activity: Optional[ActivitySession] = None
    history: List[ActivitySession] = field(default_factory=list)

@dataclass
class LanguageContext:
    spoken_language: str = "en"
    preferred_response_language: str = "en"
    script: str = "Latin"
    locale: str = "en-US"

@dataclass
class UnifiedContext:
    """
    The complete state of the world at any given millisecond.
    Provides all necessary context to the Intent and LLM engines.
    """
    timestamp: float
    system_state: str
    current_task: Optional[str]
    language_context: LanguageContext = field(default_factory=LanguageContext)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    memory_context: Dict[str, Any] = field(default_factory=dict)
    desktop_context: Dict[str, Any] = field(default_factory=dict)
    vision_context: Dict[str, Any] = field(default_factory=dict)
    hardware_context: Dict[str, Any] = field(default_factory=dict)
    world_state: Optional[WorldState] = None
    activity_buffer: RecentActivityBuffer = field(default_factory=RecentActivityBuffer)
    goal_context: ActiveGoalContext = field(default_factory=ActiveGoalContext)
