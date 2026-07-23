import logging
from typing import Optional
from desktop.character.behavior.script.behavior_script import BehaviorScript
from desktop.character.behavior.speech.speech_context import SpeechTimeline, SpeechContext
from desktop.character.runtime.runtime.runtime_controller import RuntimeController
from desktop.character.runtime.scene.character_scene_manager import CharacterSceneManager

logger = logging.getLogger(__name__)

class CharacterRuntime:
    """
    S36B-R1: Master Character Runtime Playback Engine facade containing internal CharacterSceneManager.
    The ONLY runtime responsible for rendering, playing, and synchronizing Character behaviors.
    NEVER performs intent planning, behavior selection, personality decisions, voice synthesis, or capability execution.
    Consumes ONLY BehaviorScript, SpeechTimeline, and Character Studio assets.
    """
    def __init__(self):
        self.controller = RuntimeController()
        self.scene_manager = CharacterSceneManager()
        logger.info("CharacterRuntime Playback Engine & Scene Manager initialized cleanly.")

    def start(self):
        self.controller.start()

    def stop(self):
        self.controller.stop()

    def execute_script(self, script: BehaviorScript, speech_context: Optional[SpeechContext] = None):
        self.controller.execute_script(script, speech_context)

    def tick(self, dt: float = 0.071) -> Optional[str]:
        return self.controller.tick(dt)

    def set_debug_mode(self, enabled: bool):
        self.controller.window.debug_mode = enabled

    def dock_to_edge(self, edge: str = "right"):
        self.controller.window.dock_to_edge(edge)

    @property
    def metrics(self):
        return self.controller.metrics
