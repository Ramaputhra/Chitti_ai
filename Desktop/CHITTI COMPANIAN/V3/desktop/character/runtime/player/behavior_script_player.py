import logging
from typing import Optional
from desktop.character.behavior.script.behavior_script import BehaviorScript
from desktop.character.behavior.compiler.behavior_timeline_compiler import BehaviorTimelineCompiler
from desktop.character.behavior.speech.speech_context import SpeechContext
from desktop.character.runtime.player.behavior_timeline_player import BehaviorTimelinePlayer

logger = logging.getLogger(__name__)

class BehaviorScriptPlayer:
    """
    S36B: Behavior Script Player executing declarative BehaviorScript objects by compiling them to BehaviorTimeline.
    """
    def __init__(self, timeline_player: BehaviorTimelinePlayer):
        self.timeline_player = timeline_player
        self.compiler = BehaviorTimelineCompiler()

    def play_script(self, script: BehaviorScript, speech_context: Optional[SpeechContext] = None):
        logger.info(f"[BehaviorScriptPlayer] Executing script '{script.script_id}' for intent '{script.intent_name}'")
        timeline = self.compiler.compile(script, speech_context)
        self.timeline_player.play_timeline(timeline)

    def update(self, dt: float) -> Optional[str]:
        return self.timeline_player.update(dt)
