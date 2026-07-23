from typing import Optional
from desktop.character.runtime.scene.character_scene import CharacterScene, ScenePriority
from desktop.character.runtime.scene.scene_context import SceneContext

class ScenePolicyEngine:
    """
    S36B-R1: Policy engine evaluating runtime context, scene priorities, and recovery rules.
    Does NOT modify BehaviorScript or Behavior IDs.
    """
    PRIORITY_LEVELS = {
        CharacterScene.ERROR: 7,
        CharacterScene.WARNING: 6,
        CharacterScene.REMINDER: 5,
        CharacterScene.PRESENTING: 4,
        CharacterScene.WORKING: 3,
        CharacterScene.NAVIGATING: 3,
        CharacterScene.SEARCHING: 3,
        CharacterScene.TALKING: 2,
        CharacterScene.IDLE: 1
    }

    def determine_scene(self, context: SceneContext) -> CharacterScene:
        if context.reminder_active:
            return CharacterScene.REMINDER
        if context.presentation_active:
            return CharacterScene.PRESENTING
        if context.navigation_active:
            return CharacterScene.NAVIGATING
        if context.execution_active:
            return CharacterScene.WORKING
        if context.speech_active:
            return CharacterScene.TALKING
        if context.wakeword_active:
            return CharacterScene.LISTENING
        return CharacterScene.IDLE

    def should_interrupt_scene(self, current: CharacterScene, target: CharacterScene) -> bool:
        p1 = self.PRIORITY_LEVELS.get(current, 1)
        p2 = self.PRIORITY_LEVELS.get(target, 1)
        return p2 > p1
