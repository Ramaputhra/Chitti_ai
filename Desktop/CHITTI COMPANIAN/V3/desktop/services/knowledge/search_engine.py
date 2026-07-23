from typing import Any, Dict, List

from desktop.platform.shared.interfaces.knowledge_repository import IKnowledgeRepository
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.search_engine import ISearchEngine, SearchMode
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.artifact import Artifact


class SearchEngine(ISearchEngine):
    def __init__(self, repository: IKnowledgeRepository, logger: ILoggingService) -> None:
        self.repository = repository
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str: return "SearchEngine"

    @property
    def state(self) -> ServiceState: return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info("SearchEngine initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> Dict[str, Any]:
        return {"status": "Healthy"}

    def search(self, query: str, mode: SearchMode = SearchMode.KEYWORD) -> List[Artifact]:
        self.logger.info(f"Searching Knowledge Repository using {mode.name}: '{query}'")
        # In a complete implementation, this queries the underlying stores via the repository
        return []
