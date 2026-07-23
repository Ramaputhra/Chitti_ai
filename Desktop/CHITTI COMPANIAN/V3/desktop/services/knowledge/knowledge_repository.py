from typing import Any, Dict

from desktop.platform.shared.interfaces.knowledge_repository import IKnowledgeRepository
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState


class KnowledgeRepository(IKnowledgeRepository):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "KnowledgeRepository"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> Dict[str, Any]:
        return {"status": "Healthy"}
