import logging
from typing import Optional, List
from desktop.character.identity.runtime.identity_manager import IdentityManager
from desktop.character.identity.runtime.identity_loader import IdentityProfile

logger = logging.getLogger(__name__)

class IdentityRuntime:
    """
    S36C: Master Identity Runtime facade.
    The ONLY canonical source of truth for Character Name, Identity, Biography, Mission, Philosophy,
    Beliefs, Creator Information, Speech Rules, Self Knowledge, Capabilities, Limitations, and Canonical Self Responses.
    LLM NEVER invents these facts.
    """
    def __init__(self, profiles_root: Optional[str] = None):
        self.manager = IdentityManager(profiles_root=profiles_root)
        logger.info("Identity Runtime Platform initialized cleanly.")

    @property
    def active_profile(self) -> Optional[IdentityProfile]:
        return self.manager.active_profile

    def get_canonical_response(self, question: str) -> Optional[str]:
        return self.manager.get_canonical_response(question)

    def build_prompt_context(self, sections: Optional[List[str]] = None) -> str:
        return self.manager.build_prompt_context(sections)

    def reload_identity(self) -> bool:
        if self.active_profile:
            return self.manager.load_profile("default")
        return False

    @property
    def metrics(self):
        return self.manager.metrics
