from typing import Dict, List, Optional
from desktop.models.memory import Fact, WorkingMemoryEntry, SessionState
from desktop.app.memory_contracts import IMemoryProvider

class DictMemoryProvider(IMemoryProvider):
    """
    In-memory storage provider for Sprint 78.
    Implements the append-only storage lifecycle without strict disk durability.
    """
    def __init__(self):
        # session_id -> List[InteractionRecord]
        self._interactions: Dict[str, List[InteractionRecord]] = {}
        # workflow_id -> Dict[key, WorkingMemoryEntry]
        self._working_memory: Dict[str, Dict[str, WorkingMemoryEntry]] = {}
        # session_id -> SessionState
        self._session_states: Dict[str, SessionState] = {}
        # interaction_id -> InteractionRecord
        self._interaction_lookup: Dict[str, InteractionRecord] = {}

    def append_interaction(self, record: InteractionRecord) -> None:
        if record.session_id not in self._interactions:
            self._interactions[record.session_id] = []
        self._interactions[record.session_id].append(record)
        self._interaction_lookup[record.interaction_id] = record

    def get_recent_interactions(self, session_id: str, limit: int = 50) -> List[InteractionRecord]:
        return self._interactions.get(session_id, [])[-limit:]

    def get_interaction(self, interaction_id: str) -> Optional[InteractionRecord]:
        return self._interaction_lookup.get(interaction_id)

    def set_working_memory(self, entry: WorkingMemoryEntry) -> None:
        if entry.workflow_id not in self._working_memory:
            self._working_memory[entry.workflow_id] = {}
        self._working_memory[entry.workflow_id][entry.key] = entry

    def get_working_memory(self, workflow_id: str, key: str) -> Optional[WorkingMemoryEntry]:
        wf_mem = self._working_memory.get(workflow_id)
        if wf_mem:
            return wf_mem.get(key)
        return None

    def get_all_working_memory(self, workflow_id: str) -> List[WorkingMemoryEntry]:
        wf_mem = self._working_memory.get(workflow_id)
        if wf_mem:
            return list(wf_mem.values())
        return []

    def clear_working_memory(self, workflow_id: str, key: Optional[str] = None) -> None:
        if workflow_id in self._working_memory:
            if key is None:
                del self._working_memory[workflow_id]
            else:
                self._working_memory[workflow_id].pop(key, None)

    def set_session_state(self, session_id: str, state: SessionState) -> None:
        self._session_states[session_id] = state

    def get_session_state(self, session_id: str) -> SessionState:
        return self._session_states.get(session_id, SessionState.ACTIVE)

    def flush(self) -> None:
        # In a real SQLiteProvider, this commits the transaction.
        # Here, it's a no-op since it's an in-memory dict.
        pass
