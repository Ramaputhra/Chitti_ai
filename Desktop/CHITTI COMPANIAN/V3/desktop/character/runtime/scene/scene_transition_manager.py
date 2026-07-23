import logging
from typing import Tuple
from desktop.character.runtime.scene.character_scene import CharacterScene
from desktop.character.runtime.scene.scene_validator import SceneValidator

logger = logging.getLogger(__name__)

class SceneTransitionManager:
    """
    S36B-R1: Validates and manages scene transitions and coordinates window state animations.
    """
    def __init__(self):
        self.validator = SceneValidator()

    def transition_scene(self, current: CharacterScene, target: CharacterScene) -> Tuple[bool, CharacterScene]:
        is_valid, msg = self.validator.validate_transition(current, target)
        if is_valid:
            logger.info(f"[SceneTransitionManager] Transitioning scene: {current.value} -> {target.value}")
            return True, target
        logger.warning(f"[SceneTransitionManager] Scene transition blocked: {msg}")
        return False, current
