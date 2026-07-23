from typing import Dict, List, Tuple
from desktop.character.behavior.script.behavior_script import ScriptInstruction, LoopCondition, TriggerCondition

class IntentBehaviorMapper:
    """
    S34B-R1: Decoupled Intent to Behavior Performance Mapper.
    Composes general character performance behaviors (TalkingExplain, PointScreen, Smile, WriteReminder)
    rather than hardcoded domain talking behaviors.
    """
    INTENT_COMPOSITION_MAP: Dict[str, List[ScriptInstruction]] = {
        "OPEN_BROWSER": [
            ScriptInstruction(behavior_id="CHR_TALK_EXPLAIN_001", behavior_name="TalkingExplain", loop_condition=LoopCondition("LoopUntilSpeechEnds")),
            ScriptInstruction(behavior_id="CHR_SUCC_SMILE_001", behavior_name="Smile")
        ],
        "WEATHER": [
            ScriptInstruction(behavior_id="CHR_TALK_EXPLAIN_001", behavior_name="TalkingExplain", loop_condition=LoopCondition("LoopUntilSpeechEnds"))
        ],
        "PRODUCTIVITY_PRESENTATION": [
            ScriptInstruction(behavior_id="CHR_TRANS_SLIDE_IN_L_001", behavior_name="SlideInLeft"),
            ScriptInstruction(behavior_id="CHR_GREET_MORNING_001", behavior_name="GreetingMorning"),
            ScriptInstruction(behavior_id="CHR_TALK_EXPLAIN_001", behavior_name="TalkingExplain", loop_condition=LoopCondition("LoopUntilSpeechEnds")),
            ScriptInstruction(behavior_id="CHR_GEST_POINT_SCR_001", behavior_name="PointScreen", trigger_condition=TriggerCondition("SentenceBoundary", 2)),
            ScriptInstruction(behavior_id="CHR_SUCC_SMILE_001", behavior_name="Smile"),
            ScriptInstruction(behavior_id="CHR_IDLE_001", behavior_name="Idle", trigger_condition=TriggerCondition("SpeechCompleted"))
        ],
        "REMINDER_CREATE": [
            ScriptInstruction(behavior_id="CHR_REM_WRITE_001", behavior_name="WriteReminder"),
            ScriptInstruction(behavior_id="CHR_TALK_EXPLAIN_001", behavior_name="TalkingExplain", loop_condition=LoopCondition("LoopUntilSpeechEnds"))
        ],
        "SEARCH_FILES": [
            ScriptInstruction(behavior_id="CHR_WORK_SEARCH_FILES_001", behavior_name="SearchingFiles", loop_condition=LoopCondition("LoopUntilExecutionCompletes")),
            ScriptInstruction(behavior_id="CHR_TALK_EXPLAIN_001", behavior_name="TalkingExplain", loop_condition=LoopCondition("LoopUntilSpeechEnds"))
        ],
        "WORKFLOW_RUNNING": [
            ScriptInstruction(behavior_id="CHR_WORK_TYPING_001", behavior_name="TypingLaptop", loop_condition=LoopCondition("LoopUntilExecutionCompletes")),
            ScriptInstruction(behavior_id="CHR_SUCC_THUMBSUP_001", behavior_name="ThumbsUp", trigger_condition=TriggerCondition("ExecutionCompleted"))
        ],
        "OCR": [
            ScriptInstruction(behavior_id="CHR_VIS_OCR_001", behavior_name="OCRReading", loop_condition=LoopCondition("LoopUntilExecutionCompletes")),
            ScriptInstruction(behavior_id="CHR_TALK_EXPLAIN_001", behavior_name="TalkingExplain", loop_condition=LoopCondition("LoopUntilSpeechEnds"))
        ],
        "VISION": [
            ScriptInstruction(behavior_id="CHR_VIS_INSPECT_001", behavior_name="InspectImage"),
            ScriptInstruction(behavior_id="CHR_TALK_EXPLAIN_001", behavior_name="TalkingExplain", loop_condition=LoopCondition("LoopUntilSpeechEnds"))
        ],
        "NAVIGATION": [
            ScriptInstruction(behavior_id="CHR_NAV_ROUTE_001", behavior_name="ShowRoute"),
            ScriptInstruction(behavior_id="CHR_TALK_EXPLAIN_001", behavior_name="TalkingExplain", loop_condition=LoopCondition("LoopUntilSpeechEnds"))
        ]
    }

    def map_intent_to_instructions(self, intent_name: str) -> List[ScriptInstruction]:
        key = intent_name.upper()
        if key in self.INTENT_COMPOSITION_MAP:
            return self.INTENT_COMPOSITION_MAP[key]
        return [
            ScriptInstruction(behavior_id="CHR_TALK_EXPLAIN_001", behavior_name="TalkingExplain", loop_condition=LoopCondition("LoopUntilSpeechEnds")),
            ScriptInstruction(behavior_id="CHR_IDLE_001", behavior_name="Idle")
        ]
