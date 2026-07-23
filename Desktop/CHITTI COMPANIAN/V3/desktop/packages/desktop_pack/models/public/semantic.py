from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Window:
    """Semantic representation of a desktop window."""
    window_id: str
    title: str
    app_name: str
    is_focused: bool
    is_minimized: bool
    is_maximized: bool
    bounds: Dict[str, int] # x, y, width, height
    display_id: str

@dataclass
class Display:
    """Semantic representation of a monitor."""
    display_id: str
    is_primary: bool
    resolution: Dict[str, int] # width, height
    dpi: float

@dataclass
class ClipboardData:
    """Semantic representation of clipboard content."""
    content_type: str # text, image, file
    text_content: Optional[str] = None
    file_paths: List[str] = field(default_factory=list)

@dataclass
class RunningApplication:
    """Semantic representation of a running process."""
    process_id: int
    name: str
    cpu_usage: float
    memory_mb: float
    main_window_id: Optional[str] = None

@dataclass
class DesktopOverview:
    """Aggregated semantic representation of the current desktop state."""
    active_display: Display
    all_displays: List[Display]
    active_window: Optional[Window]
    running_apps: List[RunningApplication]
    clipboard_preview: Optional[ClipboardData]
