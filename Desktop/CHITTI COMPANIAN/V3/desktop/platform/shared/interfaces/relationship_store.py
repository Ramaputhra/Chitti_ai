from typing import List

from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.knowledge import KnowledgeEdge


class RelationshipRegistry:
    def __init__(self) -> None:
        self._allowed_types = {
            "contains", "references", "generated_from", "summarized_by", 
            "mentions", "belongs_to", "depends_on", "derived_from", 
            "duplicate_of", "same_as", "replaces", "updates"
        }

    def is_valid(self, rel_type: str) -> bool:
        return rel_type in self._allowed_types

    def register(self, rel_type: str) -> None:
        self._allowed_types.add(rel_type)


class IRelationshipStore(IService):
    """
    Manages KnowledgeEdges representing relationships between Artifacts/Entities.
    """
    def get_registry(self) -> RelationshipRegistry:
        ...

    def create_edge(self, edge: KnowledgeEdge) -> None:
        ...

    def get_edges_for_node(self, node_id: str) -> List[KnowledgeEdge]:
        ...
