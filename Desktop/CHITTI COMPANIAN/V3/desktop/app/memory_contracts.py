from abc import ABC, abstractmethod
from typing import Any, List, Optional
from desktop.models.memory import InteractionRecord, WorkingMemoryEntry, MemorySnapshot, SessionState

class IMemoryProvider(ABC):
    """
    Storage abstraction layer for Memory (e.g., Dict, SQLite, Cloud).
    Owned by the MemoryRuntime, decoupled from the Planner.
    """
    @abstractmethod
    def append_interaction(self, record: InteractionRecord) -> None: pass

    @abstractmethod
    def get_recent_interactions(self, session_id: str, limit: int = 50) -> List[InteractionRecord]: pass

    @abstractmethod
    def get_interaction(self, interaction_id: str) -> Optional[InteractionRecord]: pass

    @abstractmethod
    def set_working_memory(self, entry: WorkingMemoryEntry) -> None: pass

    @abstractmethod
    def get_working_memory(self, workflow_id: str, key: str) -> Optional[WorkingMemoryEntry]: pass
    
    @abstractmethod
    def get_all_working_memory(self, workflow_id: str) -> List[WorkingMemoryEntry]: pass

    @abstractmethod
    def clear_working_memory(self, workflow_id: str, key: Optional[str] = None) -> None: pass

    @abstractmethod
    def set_session_state(self, session_id: str, state: SessionState) -> None: pass
    
    @abstractmethod
    def get_session_state(self, session_id: str) -> SessionState: pass

    @abstractmethod
    def flush(self) -> None: pass

class IMemoryService(ABC):
    """
    Dependency Injected contract for Planners to interact with Memory semantics.
    """
    @abstractmethod
    def append_interaction(self, session_id: str, interaction_id: str, role: str, content: str, metadata: dict = None) -> InteractionRecord: pass

    @abstractmethod
    def get_recent_interactions(self, session_id: str, limit: int = 50) -> List[InteractionRecord]: pass

    @abstractmethod
    def set_working_memory(self, workflow_id: str, key: str, value: Any, ttl_seconds: int = None) -> WorkingMemoryEntry: pass

    @abstractmethod
    def get_working_memory(self, workflow_id: str, key: str) -> Any: pass

    @abstractmethod
    def clear_working_memory(self, workflow_id: str, key: Optional[str] = None) -> None: pass

    @abstractmethod
    def close_session(self, session_id: str) -> None: pass

    @abstractmethod
    def snapshot(self, session_id: str, workflow_id: str) -> MemorySnapshot: pass
