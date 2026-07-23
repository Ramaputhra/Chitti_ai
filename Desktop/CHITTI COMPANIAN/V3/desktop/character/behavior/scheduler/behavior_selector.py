from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
from desktop.character.behavior.state.character_state import CharacterState
from desktop.character.behavior.mapping.intent_behavior_mapper import IntentBehaviorMapper

@dataclass
class BehaviorContext:
    """
    S34B: Behavior Context containing environment, workflow, presentation, and speech state.
    """
    current_state: CharacterState = CharacterState.BOOT
    current_intent: Optional[str] = None
    current_emotion: str = "NEUTRAL"
    current_workflow: Optional[str] = None
    current_presentation: Optional[str] = None
    speech_active: bool = False
    execution_active: bool = False
    wakeword_active: bool = False
    reminder_active: bool = False
    navigation_active: bool = False
    vision_active: bool = False
    browser_active: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class BehaviorSelector:
    """
    S34B: Selects appropriate CHR_ behaviors based on BehaviorContext, intent, and speech state.
    """
    def __init__(self):
        self.mapper = IntentBehaviorMapper()

    def select_behaviors(self, context: BehaviorContext) -> List[Tuple[str, str]]:
        if context.current_intent:
            return self.mapper.map_intent(context.current_intent)

        if context.speech_active:
            return [("CHR_TALK_EXPLAIN_001", "TalkingExplain")]

        if context.execution_active:
            return [("CHR_WORK_TYPING_001", "TypingLaptop")]

        if context.wakeword_active:
            return [("CHR_LISTEN_001", "Listening")]

        return [("CHR_IDLE_001", "Idle")]
