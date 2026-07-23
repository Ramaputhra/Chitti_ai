from enum import Enum, auto
from typing import List

from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.artifact import Artifact


class SearchMode(Enum):
    KEYWORD = auto()
    GRAPH = auto()
    SEMANTIC = auto()


class ISearchEngine(IService):
    """
    Decoupled search abstraction that executes queries across the KnowledgeRepository.
    Supports Keyword, Graph Traversal, and (future) Semantic/Embedding search modes.
    """
    def search(self, query: str, mode: SearchMode = SearchMode.KEYWORD) -> List[Artifact]:
        ...
