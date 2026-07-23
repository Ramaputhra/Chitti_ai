import os
import json
from typing import Tuple, List, Dict, Any

class IdentityValidator:
    """
    S36C-R1: Validates identity schema, required files, metadata fields, and markdown document presence.
    Ensures wake_names and wake_phrases are strictly ABSENT from identity.json.
    """
    REQUIRED_FILES = [
        "identity.json", "biography.md", "mission.md", "philosophy.md",
        "beliefs.md", "creator_profile.md", "speech_rules.md",
        "self_knowledge.md", "boundaries.md", "capabilities.md",
        "limitations.md", "greetings.md", "canonical_responses.md"
    ]

    def validate_profile_directory(self, profile_dir: str) -> Tuple[bool, List[str]]:
        errors = []
        if not os.path.exists(profile_dir) or not os.path.isdir(profile_dir):
            return False, [f"Directory '{profile_dir}' does not exist."]

        for fn in self.REQUIRED_FILES:
            fp = os.path.join(profile_dir, fn)
            if not os.path.exists(fp):
                errors.append(f"Missing required identity document: '{fn}'")

        # Validate identity.json
        json_path = os.path.join(profile_dir, "identity.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                required_keys = ["character_id", "display_name", "creator", "platform_version", "identity_version", "profile_version"]
                for k in required_keys:
                    if k not in data:
                        errors.append(f"identity.json missing required field: '{k}'")
                
                # Check forbidden wake configuration fields
                forbidden_keys = ["wake_names", "wake_phrases", "wakeword"]
                for fk in forbidden_keys:
                    if fk in data:
                        errors.append(f"Forbidden wake field '{fk}' found in identity.json. Identity must not contain wake configuration.")

                if data.get("display_name") != "CHITTI":
                    errors.append(f"Display name must be clean 'CHITTI' without version suffixes (Got: '{data.get('display_name')}').")

            except Exception as e:
                errors.append(f"Failed to parse identity.json: {str(e)}")

        return len(errors) == 0, errors
