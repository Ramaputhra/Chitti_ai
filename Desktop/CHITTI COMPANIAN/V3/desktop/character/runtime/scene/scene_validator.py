from typing import Dict, Set, Tuple
from desktop.character.runtime.scene.character_scene import CharacterScene

class SceneValidator:
    """
    S36B-R1: Validates legal CharacterScene transitions inside Character Runtime.
    """
    ALL_OPERATIONAL_SCENES = {
        CharacterScene.BOOT, CharacterScene.WAKE, CharacterScene.GREETING,
        CharacterScene.LISTENING, CharacterScene.THINKING, CharacterScene.TALKING,
        CharacterScene.WORKING, CharacterScene.PRESENTING, CharacterScene.SEARCHING,
        CharacterScene.NAVIGATING, CharacterScene.REMINDER, CharacterScene.SUCCESS,
        CharacterScene.WARNING, CharacterScene.ERROR, CharacterScene.IDLE,
        CharacterScene.SLEEP, CharacterScene.EDGE_DOT, CharacterScene.HIDDEN
    }

    VALID_TRANSITIONS: Dict[CharacterScene, Set[CharacterScene]] = {
        CharacterScene.BOOT: ALL_OPERATIONAL_SCENES,
        CharacterScene.WAKE: ALL_OPERATIONAL_SCENES,
        CharacterScene.GREETING: ALL_OPERATIONAL_SCENES,
        CharacterScene.LISTENING: ALL_OPERATIONAL_SCENES,
        CharacterScene.THINKING: ALL_OPERATIONAL_SCENES,
        CharacterScene.TALKING: ALL_OPERATIONAL_SCENES,
        CharacterScene.WORKING: ALL_OPERATIONAL_SCENES,
        CharacterScene.PRESENTING: ALL_OPERATIONAL_SCENES,
        CharacterScene.SEARCHING: ALL_OPERATIONAL_SCENES,
        CharacterScene.NAVIGATING: ALL_OPERATIONAL_SCENES,
        CharacterScene.REMINDER: ALL_OPERATIONAL_SCENES,
        CharacterScene.SUCCESS: ALL_OPERATIONAL_SCENES,
        CharacterScene.WARNING: ALL_OPERATIONAL_SCENES,
        CharacterScene.ERROR: ALL_OPERATIONAL_SCENES,
        CharacterScene.IDLE: ALL_OPERATIONAL_SCENES,
        CharacterScene.SLEEP: ALL_OPERATIONAL_SCENES,
        CharacterScene.EDGE_DOT: ALL_OPERATIONAL_SCENES,
        CharacterScene.HIDDEN: ALL_OPERATIONAL_SCENES
    }

    def validate_transition(self, current: CharacterScene, target: CharacterScene) -> Tuple[bool, str]:
        allowed = self.VALID_TRANSITIONS.get(current, set())
        if target in allowed or target == current:
            return True, "Transition allowed"
        return False, f"Illegal scene transition: {current.value} -> {target.value}"
