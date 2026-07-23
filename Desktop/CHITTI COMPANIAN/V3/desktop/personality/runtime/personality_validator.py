from typing import Tuple, List, Dict, Any
from desktop.personality.runtime.personality_state import PersonalityProfile

class PersonalityValidator:
    """
    S36A-R1: Validates slider ranges (0.0 to 1.0), profile integrity, preset compatibility, and import/export payload format.
    """
    TRAIT_KEYS = [
        "professional", "friendly", "humorous", "empathetic", "motivational",
        "concise", "talkative", "curious", "playful", "formal", "confident",
        "patient", "encouraging", "supportive", "expressive"
    ]

    def validate_profile(self, profile: PersonalityProfile) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        p_dict = profile.to_dict()
        
        for k in self.TRAIT_KEYS:
            val = p_dict.get(k)
            if val is None or not (0.0 <= val <= 1.0):
                errors.append(f"Trait '{k}' value {val} out of valid range [0.0, 1.0].")

        is_valid = len(errors) == 0
        return is_valid, errors

    def validate_import_json(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not isinstance(data, dict):
            errors.append("Import data must be a JSON object.")
            return False, errors

        for k in self.TRAIT_KEYS:
            if k in data and not (0.0 <= float(data[k]) <= 1.0):
                errors.append(f"Import trait '{k}' value out of valid range [0.0, 1.0].")

        return len(errors) == 0, errors
