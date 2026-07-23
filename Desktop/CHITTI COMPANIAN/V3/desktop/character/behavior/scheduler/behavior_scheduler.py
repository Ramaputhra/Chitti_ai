import time
import logging
from typing import Optional, List
from desktop.character.behavior.state.character_state import CharacterState
from desktop.character.behavior.state.behavior_state_machine import BehaviorStateMachine
from desktop.character.behavior.mapping.intent_behavior_mapper import IntentBehaviorMapper
from desktop.character.behavior.script.behavior_script import BehaviorScript, ScriptInstruction
from desktop.character.behavior.script.behavior_script_validator import BehaviorScriptValidator
from desktop.character.behavior.compiler.behavior_timeline_compiler import BehaviorTimelineCompiler
from desktop.character.behavior.timeline.behavior_timeline import BehaviorTimeline
from desktop.character.behavior.speech.speech_context import SpeechContext

logger = logging.getLogger(__name__)

class BehaviorScheduler:
    """
    S34B-R1: Event-Driven Character Behavior Scheduler producing BehaviorScript as primary output.
    Contains ZERO rendering, PNG playback, or lip sync logic.
    """
    def __init__(self):
        self.state_machine = BehaviorStateMachine(CharacterState.BOOT)
        self.mapper = IntentBehaviorMapper()
        self.validator = BehaviorScriptValidator()
        self.compiler = BehaviorTimelineCompiler()
        self.simulation_mode = False

    def schedule_script_for_intent(
        self,
        intent_name: str,
        session_id: str = "sess_default",
        speech_context: Optional[SpeechContext] = None
    ) -> BehaviorScript:
        if self.state_machine.current_state == CharacterState.BOOT:
            self.state_machine.transition_to(CharacterState.WAKE)
        target_st = CharacterState.TALKING if speech_context else CharacterState.WORKING
        if self.state_machine.can_transition(target_st):
            self.state_machine.transition_to(target_st)

        instructions = self.mapper.map_intent_to_instructions(intent_name)
        script_id = f"script_{intent_name.lower()}_{int(time.time() * 1000)}"
        script = BehaviorScript(
            script_id=script_id,
            session_id=session_id,
            intent_name=intent_name,
            instructions=instructions
        )

        is_valid, errors = self.validator.validate_script(script)
        if not is_valid:
            logger.warning(f"[BehaviorScheduler] Script validation warnings: {errors}")

        return script

    def schedule_timeline_for_intent(
        self,
        intent_name: str,
        session_id: str = "sess_default",
        speech_context: Optional[SpeechContext] = None
    ) -> BehaviorTimeline:
        script = self.schedule_script_for_intent(intent_name, session_id, speech_context)
        timeline = self.compiler.compile(script, speech_context)

        if self.simulation_mode:
            script.print_script()
            timeline.print_simulation()

        return timeline
