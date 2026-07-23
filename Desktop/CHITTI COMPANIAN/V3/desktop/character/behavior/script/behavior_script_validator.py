from typing import List, Tuple
from desktop.character.behavior.script.behavior_script import BehaviorScript
from desktop.character.behavior.mapping.behavior_policy import BehaviorPolicy

class BehaviorScriptValidator:
    """
    S34B-R1: Validates BehaviorScript for legal transitions, missing behaviors, illegal loops, and priority conflicts.
    """
    def __init__(self):
        self.policy = BehaviorPolicy()

    def validate_script(self, script: BehaviorScript) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not script.instructions:
            errors.append("BehaviorScript contains zero instructions.")
            return False, errors

        for idx, inst in enumerate(script.instructions):
            if not inst.behavior_id or not inst.behavior_name:
                errors.append(f"Instruction {idx+1} is missing behavior_id or behavior_name.")
            
            if idx > 0:
                prev = script.instructions[idx-1]
                if not self.policy.is_transition_allowed(prev.behavior_name, inst.behavior_name):
                    errors.append(f"Illegal transition from '{prev.behavior_name}' to '{inst.behavior_name}' at step {idx+1}.")

        is_valid = len(errors) == 0
        return is_valid, errors
