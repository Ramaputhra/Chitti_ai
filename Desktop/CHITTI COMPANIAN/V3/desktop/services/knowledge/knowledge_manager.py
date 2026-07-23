from typing import Any, Dict

from desktop.platform.shared.interfaces.knowledge_manager import IKnowledgeManager
from desktop.platform.shared.interfaces.knowledge_repository import IKnowledgeRepository
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.session import ConversationSession


class KnowledgeManager(IKnowledgeManager):
    def __init__(self, repository: IKnowledgeRepository, logger: ILoggingService) -> None:
        self.repository = repository
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "KnowledgeManager"

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

    def process_session(self, session: ConversationSession) -> None:
        self.logger.info(f"Processing knowledge snapshot for session {session.session_id}")
        # In the future, extract execution results, update the repository, and attach the snapshot.
