import enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

class CurrentIntent(enum.Enum):
    WRITING = "writing"
    READING = "reading"
    CODING = "coding"
    SHOPPING = "shopping"
    WATCHING_VIDEO = "watching_video"
    DESIGNING = "designing"
    EDITING_PHOTO = "editing_photo"
    BROWSING = "browsing"
    UNKNOWN = "unknown"

@dataclass
class ScreenObservation:
    """The fused input representing all deterministic and raw sensor data."""
    screenshot_path: Optional[str]
    ui_tree: Dict[str, Any]
    ocr_text: str
    window_metadata: Dict[str, Any]
    clipboard_text: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ScreenModel:
    """The canonical semantic model of the screen (Rule 130)."""
    active_window: str
    application: str
    document: Optional[str]
    selection: Optional[str]
    controls: List[Dict[str, Any]]
    relationships: List[Dict[str, str]]
    tasks: List[str] # e.g. "User is editing Python code"
    current_intent: CurrentIntent
    confidence: float
    perception_quality: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ScreenDiff:
    """Captures semantic changes to avoid re-summarizing unchanged screens."""
    previous_timestamp: datetime
    current_timestamp: datetime
    added_elements: List[Dict[str, Any]]
    removed_elements: List[Dict[str, Any]]
    intent_changed: bool
    summary_of_change: str

@dataclass
class ObservationResult:
    """The final payload returned to Workflow/Planner."""
    screen_model: ScreenModel
    evidence: Dict[str, Any]
    latency_ms: int
    quality: str
    sources: List[str] # e.g. ['UIA', 'OCR', 'Vision', 'WindowManager']
