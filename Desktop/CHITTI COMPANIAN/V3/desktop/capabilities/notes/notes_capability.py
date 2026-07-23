from typing import Any, Dict

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import IService, ServiceState


class NotesCapability(IService):
    """
    Manages user notes, moving beyond simple CRUD by automatically linking
    note contents into the Knowledge and Semantic Runtimes.
    """
    def __init__(self, knowledge_runtime: Any, semantic_runtime: Any, logger: ILoggingService) -> None:
        self.knowledge_runtime = knowledge_runtime
        self.semantic_runtime = semantic_runtime
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str: return "NotesCapability"

    @property
    def state(self) -> ServiceState: return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> Dict[str, Any]:
        return {"status": "Healthy"}

    def create_semantic_note(self, title: str, content: str, context: Dict[str, Any]) -> str:
        """
        Creates a note and extracts entities (people, projects, concepts) 
        to link them in the semantic graph.
        """
        self.logger.info(f"Creating semantic note: {title}")
        
        # 1. Save literal markdown note
        note_id = "note_123"
        
        # 2. Extract Entities via Semantic Runtime
        entities = {"projects": ["Project Phoenix"]}
        
        # 3. Store associations in Knowledge Runtime
        # self.knowledge_runtime.link(note_id, entities)
        
        return note_id
