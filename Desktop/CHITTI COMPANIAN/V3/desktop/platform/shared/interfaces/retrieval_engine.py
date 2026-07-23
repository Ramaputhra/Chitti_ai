from typing import List

from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.artifact import Artifact


class IRetrievalEngine(IService):
    """
    Executes a structured three-phase retrieval pipeline:
    1. Artifact Retrieval (via SearchEngine)
    2. Graph Traversal (expanding relationships via RelationshipStore)
    3. Context Ranking (scoring the sub-graph)
    """
    def retrieve_subgraph(self, query: str) -> List[Artifact]:
        ...
