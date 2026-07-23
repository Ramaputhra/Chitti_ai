from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union

@dataclass
class LoopCondition:
    """
    S34B-R1: Loop condition specification for BehaviorScript instructions.
    """
    condition_type: str  # "LoopUntilSpeechEnds", "LoopUntilExecutionCompletes", "LoopForever", "LoopUntilEvent", "LoopFixedCount"
    target_event: Optional[str] = None
    count: int = 1

@dataclass
class TriggerCondition:
    """
    S34B-R1: Trigger condition specification for BehaviorScript instructions.
    """
    event_type: str
    parameter: Optional[Any] = None

@dataclass
class ScriptInstruction:
    """
    S34B-R1: Individual declarative step instruction in a BehaviorScript.
    """
    behavior_id: str
    behavior_name: str
    trigger_condition: Optional[TriggerCondition] = None
    loop_condition: Optional[LoopCondition] = None
    priority: str = "NORMAL"
    interruptible: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BehaviorScript:
    """
    S34B-R1: Declarative primary output of BehaviorScheduler.
    Character Runtime translates BehaviorScript into playback timelines.
    """
    script_id: str
    session_id: str
    intent_name: str
    instructions: List[ScriptInstruction] = field(default_factory=list)

    def print_script(self):
        print(f"=== BehaviorScript [{self.script_id}] (Intent: {self.intent_name}) ===")
        for idx, inst in enumerate(self.instructions, 1):
            trig_str = f" [Trigger: {inst.trigger_condition.event_type}({inst.trigger_condition.parameter})]" if inst.trigger_condition else ""
            loop_str = f" [Loop: {inst.loop_condition.condition_type}]" if inst.loop_condition else ""
            print(f"  {idx}. [{inst.behavior_id}] {inst.behavior_name}{trig_str}{loop_str}")
        print()
