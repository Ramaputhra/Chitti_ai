import logging
from typing import Optional, List, Tuple
from desktop.character.runtime.scene.character_scene import CharacterScene
from desktop.character.runtime.scene.scene_context import SceneContext
from desktop.character.runtime.scene.scene_policy import ScenePolicyEngine
from desktop.character.runtime.scene.scene_transition_manager import SceneTransitionManager
from desktop.character.runtime.scene.scene_metrics import SceneMetrics

logger = logging.getLogger(__name__)

class CharacterSceneManager:
    """
    S36B-R1: Highest-level orchestration component INSIDE Character Runtime.
    Manages scene state, scene stack, recovery rules, window management, and telemetry history.
    Does NOT perform intent planning, capability selection, personality decisions, or voice synthesis.
    """
    def __init__(self):
        self.context = SceneContext()
        self.policy_engine = ScenePolicyEngine()
        self.transition_mgr = SceneTransitionManager()
        self.metrics = SceneMetrics()

    @property
    def current_scene(self) -> CharacterScene:
        return self.context.current_scene

    def transition_to_scene(self, target_scene: CharacterScene) -> bool:
        if target_scene == self.context.current_scene:
            return True

        if self.policy_engine.should_interrupt_scene(self.context.current_scene, target_scene) and self.context.current_scene not in (CharacterScene.IDLE, CharacterScene.HIDDEN):
            # Push interrupted operational scene to stack for recovery
            logger.info(f"[CharacterSceneManager] Interrupting '{self.context.current_scene.value}' with higher priority '{target_scene.value}'. Pushing to stack.")
            self.metrics.scene_stack.append(self.context.current_scene)

        ok, new_scene = self.transition_mgr.transition_scene(self.context.current_scene, target_scene)
        if ok:
            self.context.previous_scene = self.context.current_scene
            self.context.current_scene = new_scene
            self.metrics.record_scene_change(new_scene)
            return True
        return False

    def complete_current_scene(self):
        logger.info(f"[CharacterSceneManager] Scene '{self.context.current_scene.value}' completed.")
        if self.metrics.scene_stack:
            restored_scene = self.metrics.scene_stack.pop()
            logger.info(f"[CharacterSceneManager] Scene Recovery: Restoring interrupted scene '{restored_scene.value}' from stack.")
            self.transition_to_scene(restored_scene)
        else:
            self.transition_to_scene(CharacterScene.IDLE)

    def update_context(
        self,
        speech_active: Optional[bool] = None,
        execution_active: Optional[bool] = None,
        presentation_active: Optional[bool] = None,
        reminder_active: Optional[bool] = None,
        navigation_active: Optional[bool] = None
    ):
        if speech_active is not None:
            self.context.speech_active = speech_active
        if execution_active is not None:
            self.context.execution_active = execution_active
        if presentation_active is not None:
            self.context.presentation_active = presentation_active
        if reminder_active is not None:
            self.context.reminder_active = reminder_active
        if navigation_active is not None:
            self.context.navigation_active = navigation_active

        target_scene = self.policy_engine.determine_scene(self.context)
        if target_scene != self.context.current_scene:
            self.transition_to_scene(target_scene)
