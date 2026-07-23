from typing import List, Optional
from dataclasses import dataclass

@dataclass
class SearchResult:
    path: str
    name: str
    extension: str
    size: int
    modified_time: float
    score: float = 1.0

class IFileSystemProvider:
    """Provides abstracted file system access."""
    def search_files(self, query: str, directory: str = "~", max_results: int = 10) -> List[SearchResult]:
        raise NotImplementedError
