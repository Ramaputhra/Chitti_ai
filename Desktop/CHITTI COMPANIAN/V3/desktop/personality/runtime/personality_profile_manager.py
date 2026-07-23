import os
import json
import logging
from typing import Dict, List, Optional
from desktop.personality.runtime.personality_state import PersonalityProfile
from desktop.personality.runtime.personality_validator import PersonalityValidator

logger = logging.getLogger(__name__)

class PersonalityProfileManager:
    """
    S36A-R1: Manages canonical PersonalityProfiles, presets, persistence, import/export.
    """
    PRESETS: Dict[str, PersonalityProfile] = {
        "professional": PersonalityProfile("professional", "Professional", professional=0.9, friendly=0.4, humorous=0.1, empathetic=0.6, motivational=0.5, concise=0.8, talkative=0.3, formal=0.9, confident=0.9),
        "friendly": PersonalityProfile("friendly", "Friendly", professional=0.4, friendly=0.9, humorous=0.6, empathetic=0.9, motivational=0.8, concise=0.5, talkative=0.7, formal=0.2, confident=0.8),
        "teacher": PersonalityProfile("teacher", "Teacher", professional=0.7, friendly=0.8, humorous=0.3, empathetic=0.9, motivational=0.9, concise=0.4, talkative=0.8, patient=1.0, encouraging=0.9),
        "minimal": PersonalityProfile("minimal", "Minimal", professional=0.7, friendly=0.3, humorous=0.0, empathetic=0.3, motivational=0.2, concise=1.0, talkative=0.1, formal=0.5, confident=0.8),
        "motivational": PersonalityProfile("motivational", "Motivational", professional=0.5, friendly=0.8, humorous=0.5, empathetic=0.8, motivational=1.0, concise=0.5, talkative=0.8, confident=1.0),
        "developer": PersonalityProfile("developer", "Developer", professional=0.8, friendly=0.5, humorous=0.4, empathetic=0.4, motivational=0.5, concise=0.8, talkative=0.4, curious=0.9),
        "productivity_coach": PersonalityProfile("productivity_coach", "Productivity Coach", professional=0.8, friendly=0.7, humorous=0.3, empathetic=0.7, motivational=0.9, concise=0.7, talkative=0.6),
        "story_teller": PersonalityProfile("story_teller", "Story Teller", professional=0.3, friendly=0.9, humorous=0.7, empathetic=0.9, motivational=0.7, concise=0.2, talkative=0.9, expressive=1.0),
        "assistant": PersonalityProfile("assistant", "Assistant", professional=0.6, friendly=0.8, humorous=0.4, empathetic=0.8, motivational=0.7, concise=0.6, talkative=0.5, supportive=0.9)
    }

    def __init__(self, storage_path: Optional[str] = None):
        self.validator = PersonalityValidator()
        self._active_profile = self.PRESETS["friendly"]
        self.storage_path = storage_path or os.path.join(os.path.dirname(__file__), "personality_profile.json")
        self.load_from_file()

    @property
    def active_profile(self) -> PersonalityProfile:
        return self._active_profile

    def apply_preset(self, preset_key: str) -> bool:
        key = preset_key.lower()
        if key in self.PRESETS:
            self._active_profile = self.PRESETS[key]
            self.save_to_file()
            return True
        return False

    def update_active_traits(self, **traits) -> Tuple[bool, List[str]]:
        p_dict = self._active_profile.to_dict()
        for k, v in traits.items():
            if k in p_dict and isinstance(v, (int, float)):
                p_dict[k] = max(0.0, min(1.0, float(v)))
        
        new_prof = PersonalityProfile.from_dict(p_dict)
        valid, errors = self.validator.validate_profile(new_prof)
        if valid:
            self._active_profile = new_prof
            self.save_to_file()
            return True, []
        return False, errors

    def export_json(self) -> str:
        return json.dumps(self._active_profile.to_dict(), indent=2)

    def import_json(self, json_str: str) -> Tuple[bool, List[str]]:
        try:
            data = json.loads(json_str)
            valid, errors = self.validator.validate_import_json(data)
            if valid:
                self._active_profile = PersonalityProfile.from_dict(data)
                self.save_to_file()
                return True, []
            return False, errors
        except Exception as e:
            return False, [str(e)]

    def save_to_file(self):
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                f.write(self.export_json())
        except Exception as e:
            logger.error(f"Failed to save personality profile to file: {e}")

    def load_from_file(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.import_json(f.read())
            except Exception as e:
                logger.error(f"Failed to load personality profile from file: {e}")
