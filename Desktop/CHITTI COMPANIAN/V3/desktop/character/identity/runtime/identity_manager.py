import os
import logging
from typing import Optional, Dict, Tuple, List
from desktop.character.identity.runtime.identity_loader import IdentityLoader, IdentityProfile
from desktop.character.identity.runtime.identity_validator import IdentityValidator
from desktop.character.identity.runtime.identity_context_builder import IdentityContextBuilder
from desktop.character.identity.runtime.identity_metrics import IdentityMetrics

logger = logging.getLogger(__name__)

class IdentityManager:
    """
    S36C: Master Identity Manager orchestrating profile loading, canonical responses retrieval,
    hot reload, context building, and validation.
    """
    def __init__(self, profiles_root: Optional[str] = None):
        self.loader = IdentityLoader(profiles_root=profiles_root)
        self.validator = IdentityValidator()
        self.context_builder = IdentityContextBuilder()
        self.metrics = IdentityMetrics()
        self.active_profile: Optional[IdentityProfile] = None
        self.load_profile("default")

    def load_profile(self, profile_name: str = "default") -> bool:
        p_dir = os.path.join(self.loader.root, profile_name)
        valid, errors = self.validator.validate_profile_directory(p_dir)
        if not valid:
            logger.error(f"[IdentityManager] Identity validation failed: {errors}")
            self.metrics.validation_failures += 1
            return False

        profile = self.loader.load_profile(profile_name)
        if profile:
            self.active_profile = profile
            self.metrics.profile_load_count += 1
            return True
        return False

    def get_canonical_response(self, question: str) -> Optional[str]:
        if not self.active_profile or "canonical_responses" not in self.active_profile.documents:
            return None

        self.metrics.canonical_queries_count += 1
        q_clean = question.strip().lower()
        doc = self.active_profile.documents["canonical_responses"]

        # Parse markdown headers and answers
        current_header = ""
        current_body = []
        parsed: Dict[str, str] = {}

        for line in doc.splitlines():
            if line.startswith("## "):
                if current_header:
                    parsed[current_header.strip().lower()] = "\n".join(current_body).strip()
                current_header = line[3:].strip()
                current_body = []
            else:
                if current_header:
                    current_body.append(line)
        if current_header:
            parsed[current_header.strip().lower()] = "\n".join(current_body).strip()

        # Match query against canonical questions
        for key_q, ans in parsed.items():
            if key_q in q_clean or q_clean in key_q:
                return ans

        # Fallback keywords
        if "who are you" in q_clean or "tell me about yourself" in q_clean:
            return parsed.get("who are you?", "I am CHITTI V2, an intelligent AI desktop companion.")
        if "who created you" in q_clean or "who made you" in q_clean:
            return parsed.get("who created you?", f"I was created by {self.active_profile.creator}.")
        if "purpose" in q_clean:
            return parsed.get("what is your purpose?", self.active_profile.mission)

        return None

    def build_prompt_context(self, sections: Optional[List[str]] = None) -> str:
        self.metrics.context_build_count += 1
        return self.context_builder.build_system_identity_prompt(self.active_profile, sections)
