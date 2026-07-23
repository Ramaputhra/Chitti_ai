from typing import Any, List, Optional, Protocol

from desktop.platform.shared.models.intent import Intent


class ISkill(Protocol):
    """
    Standard interface for all CHITTI capabilities/plugins.
    """
    def id(self) -> str:
        ...

    def name(self) -> str:
        ...

    def version(self) -> str:
        ...

    def supported_intents(self) -> List[str]:
        ...

    def execute(self, intent: Intent) -> Any:
        ...

    def health_check(self) -> bool:
        ...


class ISkillRegistry(Protocol):
    """
    Maintains a list of all active skills in the system.
    """
    def register(self, skill: ISkill) -> None:
        ...

    def get_skill_for_intent(self, intent_type: str) -> Optional[ISkill]:
        ...

    def get_skill_by_id(self, skill_id: str) -> Optional[ISkill]:
        ...
