from dataclasses import dataclass, field
from typing import List

@dataclass
class DebugOverlayState:
    current_scene: str = "IDLE"
    previous_scene: str = "HIDDEN"
    scene_stack: List[str] = field(default_factory=list)
    behavior_id: str = "CHR_IDLE_001"
    frame_index: int = 1
    fps: float = 14.0
    memory_mb: float = 42.5
    playback_time: float = 0.0
    current_state: str = "Visible"

class OverlayRenderer:
    """
    S36B-R1: Extended Debug Overlay displaying Current Scene, Previous Scene, Scene Stack,
    Current Behavior, Behavior ID, FPS, Playback Time, and Window State.
    """
    def format_debug_text(self, state: DebugOverlayState) -> str:
        stack_str = " -> ".join(state.scene_stack) if state.scene_stack else "Empty"
        return (
            f"=== CHITTI CHARACTER RUNTIME DEBUG ===\n"
            f"Current Scene: {state.current_scene}\n"
            f"Prev Scene   : {state.previous_scene}\n"
            f"Scene Stack  : [{stack_str}]\n"
            f"Behavior ID  : {state.behavior_id}\n"
            f"Frame        : {state.frame_index:02d} / 14\n"
            f"FPS          : {state.fps:.1f}\n"
            f"Memory       : {state.memory_mb:.1f} MB\n"
            f"Time         : {state.playback_time:.2f}s\n"
            f"Window State : {state.current_state}"
        )
