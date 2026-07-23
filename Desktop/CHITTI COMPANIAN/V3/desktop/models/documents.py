from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class DocumentContent:
    """
    Structured Context produced by Document Intelligence (Rule 10).
    Abstracts away the raw file format, providing a uniform representation for the Planner.
    """
    markdown: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    sections: List[str] = field(default_factory=list)
    tables: List[str] = field(default_factory=list)  # Preserved structurally, often as markdown tables
    images: List[str] = field(default_factory=list)  # Placeholders for now
    page_count: int = 1
