from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

from desktop.models.companion import CompanionContext
from desktop.models.execution import ExecutionContext
from desktop.platform.shared.models.session import ConversationSession

@dataclass
class ResolvedInteraction:
    pass

@dataclass
class ConversationFocus:
    pass

@dataclass
class ConversationArtifact:
    """Base artifact structure."""
    artifact_id: str
    artifact_type: str
    capability_id: str
    timestamp: datetime
    summary: str
    structured_result: Dict[str, Any]
    referenced_entities: List[str]
    supported_followup_actions: List[str]
    presentation_available: bool
    expiration_policy: str
    confidence: float

@dataclass
class NavigationArtifact(ConversationArtifact):
    artifact_version: str = "1.0"
    origin: str = ""
    destination: str = ""
    travel_mode: str = "driving"
    route_geometry: str = ""
    route_summary: str = ""
    waypoints: List[str] = field(default_factory=list)
    traffic_snapshot: str = "moderate"
    alternative_routes: int = 0
    supported_affordances: List[str] = field(default_factory=list)
    expires_at: Optional[datetime] = None

@dataclass
class NavigationSession:
    session_id: str
    artifact_id: str
    current_waypoint: int = 0
    remaining_distance: float = 0.0
    remaining_eta: int = 0
    reroute_count: int = 0
    navigation_status: str = "started"
    arrival_state: bool = False

@dataclass
class PageSnapshot:
    headings: List[str] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    products: List[Dict[str, Any]] = field(default_factory=list)
    forms: List[Dict[str, Any]] = field(default_factory=list)
    buttons: List[str] = field(default_factory=list)
    links: List[Dict[str, str]] = field(default_factory=list)

@dataclass
class BrowserArtifact(ConversationArtifact):
    session_id: str = ""
    browser_id: str = ""
    active_tab: str = ""
    open_tabs: List[str] = field(default_factory=list)
    page_snapshot: PageSnapshot = field(default_factory=PageSnapshot)
    selected_element: Optional[str] = None
    structured_results: Dict[str, Any] = field(default_factory=dict)
    current_url: str = ""
    page_title: str = ""
    provider: str = "playwright"
    supported_affordances: List[str] = field(default_factory=list)
    expires_at: Optional[datetime] = None

@dataclass
class LayoutTree:
    paragraphs: List[Dict[str, Any]] = field(default_factory=list)
    headings: List[Dict[str, Any]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    lists: List[Dict[str, Any]] = field(default_factory=list)
    images: List[Dict[str, Any]] = field(default_factory=list)
    captions: List[Dict[str, Any]] = field(default_factory=list)
    regions: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class OCRArtifact(ConversationArtifact):
    source_window: str = ""
    capture_region: Dict[str, int] = field(default_factory=dict)
    recognized_text: str = ""
    layout_tree: LayoutTree = field(default_factory=LayoutTree)
    supported_affordances: List[str] = field(default_factory=list)
    presentation_descriptor: Optional[Dict[str, Any]] = None
    memory_candidate: Optional[Dict[str, Any]] = None

@dataclass
class Citation:
    title: str
    url: str
    provider: str
    retrieved_at: datetime
    rank: int
    confidence: float

@dataclass
class EntityDescriptor:
    id: str
    display: str
    type: str
    executable: str = ""

@dataclass
class ReferencedEntity:
    entity_id: str
    entity_type: str
    canonical_name: str
    metadata: Dict[str, Any]

@dataclass
class SearchArtifact(ConversationArtifact):
    """
    Structured retrieval artifact. 
    Maintains strict separation between raw results and deterministic entity extraction.
    """
    provider: str = ""
    query: str = ""
    results: List[Dict[str, Any]] = field(default_factory=list)
    extracted_entities: List[ReferencedEntity] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)
    supported_affordances: List[str] = field(default_factory=list)
    presentation_descriptor: Optional[Dict[str, Any]] = None
    memory_candidate: Optional[Dict[str, Any]] = None

@dataclass
class PageArtifact(ConversationArtifact):
    url: str = ""
    title: str = ""
    layout_tree: Any = None
    active_tab_id: str = ""
    affordances: List[str] = field(default_factory=list)

@dataclass
class ShoppingArtifact(PageArtifact):
    product: Any = None
    affordances: List[str] = field(default_factory=list)

@dataclass
class AuthenticationArtifact(ConversationArtifact):
    auth_state: str
    target_service: str

@dataclass
class VisionArtifact(ConversationArtifact):
    source_window: str
    capture_timestamp: datetime
    vision_layout_tree_id: str

@dataclass
class ErrorArtifact(VisionArtifact):
    error_message: str
    error_context: str
    bounding_box: Dict[str, int]

@dataclass
class TableArtifact(VisionArtifact):
    headers: List[str]
    rows: List[List[str]]
    bounding_box: Dict[str, int]

@dataclass
class DocumentArtifact(VisionArtifact):
    knowledge: Any # KnowledgeEntity

@dataclass
class ApplicationArtifact(VisionArtifact):
    ui_controls: Dict[str, Dict[str, int]]

@dataclass
class DocumentationArtifact(PageArtifact):
    article_content: str = ""
    code_blocks: List[str] = field(default_factory=list)
    affordances: List[str] = field(default_factory=list)
