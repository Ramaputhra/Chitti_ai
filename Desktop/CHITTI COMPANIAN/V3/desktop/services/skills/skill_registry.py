from typing import Any, Dict, Optional

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import IService, ServiceState
from desktop.platform.shared.interfaces.skill import ISkill, ISkillRegistry


class SkillRegistry(ISkillRegistry, IService):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._skills: Dict[str, ISkill] = {}
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "SkillRegistry"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {"registered_skills": len(self._skills)}

    def register(self, skill: ISkill) -> None:
        self._skills[skill.id()] = skill
        self.logger.info(
            f"Registered Skill: {skill.name()} v{skill.version()} supporting {skill.supported_intents()}"
        )

    def get_skill_for_intent(self, intent_type: str) -> Optional[ISkill]:
        for skill in self._skills.values():
            if intent_type in skill.supported_intents():
                return skill
        return None

    def get_skill_by_id(self, skill_id: str) -> Optional[ISkill]:
        return self._skills.get(skill_id)
