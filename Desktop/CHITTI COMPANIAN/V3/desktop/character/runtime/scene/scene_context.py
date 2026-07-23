from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from desktop.character.runtime.scene.character_scene import CharacterScene

@dataclass
class SceneContext:
    """
    S36B-R1: Context container maintained by Character Scene Manager.
    """
    current_scene: CharacterScene = CharacterScene.IDLE
    previous_scene: CharacterScene = CharacterScene.HIDDEN
    current_behavior_id: str = "CHR_IDLE_001"
    speech_active: bool = False
    execution_active: bool = False
    presentation_active: bool = False
    desktop_ui_active: bool = False
    window_state: str = "Visible"
    focus_active: bool = False
    wakeword_active: bool = False
    navigation_active: bool = False
    vision_active: bool = False
    reminder_active: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
