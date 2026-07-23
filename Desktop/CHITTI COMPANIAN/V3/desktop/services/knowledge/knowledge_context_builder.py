from typing import Any, Dict

from desktop.platform.shared.interfaces.knowledge_context_builder import IKnowledgeContextBuilder
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.retrieval_engine import IRetrievalEngine
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.session import ConversationSession


class KnowledgeContextBuilder(IKnowledgeContextBuilder):
    def __init__(self, retrieval_engine: IRetrievalEngine, logger: ILoggingService) -> None:
        self.retrieval_engine = retrieval_engine
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str: return "KnowledgeContextBuilder"

    @property
    def state(self) -> ServiceState: return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info("KnowledgeContextBuilder initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> Dict[str, Any]:
        return {"status": "Healthy"}

    def build_context(self, session: ConversationSession) -> str:
        self.logger.info("Building knowledge context for session")
        # In the future, parse session.input_audio or recognized_text
        # subgraph = self.retrieval_engine.retrieve_subgraph(query)
        return "Knowledge Context block goes here."
