from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class FileDataset:
    """Semantic dataset representing a file."""
    path: str
    size_bytes: int
    extension: str
    is_directory: bool
    last_modified: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DirectoryListing:
    """Semantic dataset representing a folder's contents."""
    directory_path: str
    files: List[FileDataset] = field(default_factory=list)
    total_size_bytes: int = 0

@dataclass
class FolderComparison:
    """Semantic dataset representing differences between two folders."""
    source_path: str
    target_path: str
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    modified: List[str] = field(default_factory=list)
