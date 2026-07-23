from typing import Any, Dict, List

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.relationship_store import IRelationshipStore, RelationshipRegistry
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.knowledge import KnowledgeEdge


class RelationshipStore(IRelationshipStore):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED
        self._registry = RelationshipRegistry()
        self._edges: List[KnowledgeEdge] = []

    @property
    def name(self) -> str: return "RelationshipStore"

    @property
    def state(self) -> ServiceState: return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info("RelationshipStore initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> Dict[str, Any]:
        return {"edges_count": len(self._edges), "registered_types": len(self._registry._allowed_types)}

    def get_registry(self) -> RelationshipRegistry:
        return self._registry

    def create_edge(self, edge: KnowledgeEdge) -> None:
        if not self._registry.is_valid(edge.relationship):
            raise ValueError(f"Unknown relationship type: {edge.relationship}")
        self._edges.append(edge)
        self.logger.info(f"Created edge: {edge.source_id} -[{edge.relationship}]-> {edge.target_id}")

    def get_edges_for_node(self, node_id: str) -> List[KnowledgeEdge]:
        return [e for e in self._edges if e.source_id == node_id or e.target_id == node_id]
