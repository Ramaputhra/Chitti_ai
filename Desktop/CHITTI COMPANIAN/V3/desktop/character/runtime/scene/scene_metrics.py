import time
from dataclasses import dataclass, field
from typing import List, Tuple
from desktop.character.runtime.scene.character_scene import CharacterScene

@dataclass
class SceneMetrics:
    """
    S36B-R1: Telemetry metrics for Character Scene Manager.
    Tracks current scene, duration, previous scene, scene stack, transition count, and scene history.
    """
    current_scene: CharacterScene = CharacterScene.HIDDEN
    previous_scene: CharacterScene = CharacterScene.HIDDEN
    scene_start_time: float = 0.0
    transition_count: int = 0
    scene_stack: List[CharacterScene] = field(default_factory=list)
    scene_history: List[Tuple[float, str]] = field(default_factory=list)

    def record_scene_change(self, new_scene: CharacterScene):
        now = time.time()
        self.previous_scene = self.current_scene
        self.current_scene = new_scene
        self.scene_start_time = now
        self.transition_count += 1
        self.scene_history.append((now, new_scene.value))
        if len(self.scene_history) > 50:
            self.scene_history.pop(0)

    @property
    def current_scene_duration(self) -> float:
        if self.scene_start_time <= 0:
            return 0.0
        return time.time() - self.scene_start_time
