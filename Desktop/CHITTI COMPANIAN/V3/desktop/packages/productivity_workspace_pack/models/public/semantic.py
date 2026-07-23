from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class WorkspaceDocument:
    document_id: str
    title: str
    content_text: str
    metadata: Dict[str, Any]
    last_modified: datetime

@dataclass
class StructuredTable:
    table_id: str
    headers: List[str]
    rows: List[List[Any]]
    statistics: Dict[str, Any]

@dataclass
class PresentationDeck:
    deck_id: str
    title: str
    slides_count: int
    speaker_notes: List[str]

@dataclass
class KnowledgeNote:
    note_id: str
    topic: str
    tags: List[str]
    content: str
    linked_entities: List[str]

@dataclass
class PDFDocument:
    pdf_id: str
    pages: int
    has_signatures: bool
    text_content: str
