from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class WindowLayout:
    app_name: str
    x: int
    y: int
    width: int
    height: int
    monitor: int = 0

@dataclass
class WindowPosition:
    x: int
    y: int
    width: int
    height: int
    maximized: bool = False

@dataclass
class WorkspaceProfile:
    """
    Defines a highly structured desktop workspace.
    """
    id: str
    name: str
    description: str = ""
    
    # Core
    applications: List[str] = field(default_factory=list)
    folders: List[str] = field(default_factory=list)
    
    # Environment
    environment_variables: Dict[str, str] = field(default_factory=dict)
    
    # Layout
    window_layouts: Dict[str, str] = field(default_factory=dict) # App name -> Monitor ID or preset
    window_positions: Dict[str, WindowPosition] = field(default_factory=dict) # App -> Position
    
    # Browser
    browser_tabs: List[str] = field(default_factory=list)
    pinned_urls: List[str] = field(default_factory=list)
    
    # Hardware/System
    power_mode: str = "balanced" # performance, balanced, battery
    audio_volume: int = -1 # -1 means don't change
    brightness: int = -1 # -1 means don't change
    
    # Orchestration
    before_actions: List[str] = field(default_factory=list) # e.g. ["Enable WiFi", "Connect VPN"]
    startup: List[str] = field(default_factory=list) # Sequence to start
    after_actions: List[str] = field(default_factory=list) # e.g. ["Arrange Windows"]
    tags: List[str] = field(default_factory=list)
