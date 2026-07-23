from dataclasses import dataclass, field
from typing import Dict, Any
from desktop.character.runtime.scene.character_scene import CharacterScene

@dataclass
class SceneEvent:
    event_type: str
    timestamp: float
    scene: CharacterScene
    payload: Dict[str, Any] = field(default_factory=dict)

class SceneEntered(SceneEvent):
    def __init__(self, timestamp: float, scene: CharacterScene):
        super().__init__("SceneEntered", timestamp, scene, {})

class SceneExited(SceneEvent):
    def __init__(self, timestamp: float, scene: CharacterScene):
        super().__init__("SceneExited", timestamp, scene, {})

class SceneChanged(SceneEvent):
    def __init__(self, timestamp: float, from_scene: CharacterScene, to_scene: CharacterScene):
        super().__init__("SceneChanged", timestamp, to_scene, {"from_scene": from_scene.value, "to_scene": to_scene.value})

class SceneInterrupted(SceneEvent):
    def __init__(self, timestamp: float, interrupted_scene: CharacterScene, interrupting_scene: CharacterScene):
        super().__init__("SceneInterrupted", timestamp, interrupted_scene, {"interrupting_scene": interrupting_scene.value})

class SceneResumed(SceneEvent):
    def __init__(self, timestamp: float, resumed_scene: CharacterScene):
        super().__init__("SceneResumed", timestamp, resumed_scene, {})

class SceneCompleted(SceneEvent):
    def __init__(self, timestamp: float, scene: CharacterScene):
        super().__init__("SceneCompleted", timestamp, scene, {})
