from typing import Optional, List
from desktop.character.identity.runtime.identity_loader import IdentityProfile

class IdentityContextBuilder:
    """
    S36C-R1: Identity Context Builder constructing compact prompt context for LLM requests
    without unnecessary token bloat.
    """
    def build_system_identity_prompt(self, profile: IdentityProfile, sections: Optional[List[str]] = None) -> str:
        if not profile:
            return ""

        parts = [
            f"Character Name: {profile.display_name} ({profile.short_name})",
            f"Creator: {profile.creator}",
            f"Platform Version: {profile.platform_version}",
            f"Identity Version: {profile.identity_version}",
            f"Mission Summary: {profile.mission}"
        ]

        target_sections = sections or ["speech_rules", "boundaries", "canonical_responses"]
        for sec in target_sections:
            if sec in profile.documents:
                parts.append(f"\n--- {sec.upper()} ---")
                parts.append(profile.documents[sec].strip())

        return "\n".join(parts)
