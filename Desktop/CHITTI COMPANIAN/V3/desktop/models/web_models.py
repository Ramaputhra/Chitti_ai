from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

class WebExecutionMode(Enum):
    SEARCH = "SEARCH"
    HTTP_FETCH = "HTTP_FETCH"
    CRAWL = "CRAWL"
    HEADLESS = "HEADLESS"
    INTERACTIVE = "INTERACTIVE"

class WebResourceType(Enum):
    SEARCH_RESULT = "SEARCH_RESULT"
    PAGE = "PAGE"
    IMAGE = "IMAGE"
    DOCUMENT = "DOCUMENT"
    VIDEO = "VIDEO"
    DOWNLOAD = "DOWNLOAD"
    LINK = "LINK"
    TABLE = "TABLE"

@dataclass
class ExtractionEvidence:
    url: str
    timestamp: float
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    content_hash: Optional[str] = None
    status_code: Optional[int] = None
    mime: Optional[str] = None
    bytes_count: Optional[int] = None

@dataclass
class WebResource:
    url: str
    title: str
    metadata: Dict[str, Any]
    evidence: Optional[ExtractionEvidence] = None

@dataclass
class WebCollection:
    resource_type: str
    results: List[WebResource]
    count: int
    source: str = ""
    timestamp: float = 0.0
    confidence: float = 1.0
    completeness: float = 1.0
    is_partial: bool = False

@dataclass
class BrowserTab:
    id: str
    url: str
    title: str
    active: bool
    loading: bool

@dataclass
class BrowserSession:
    session_id: str
    browser_type: str
    headless: bool
    profile: Optional[str]
    downloads_directory: str
    tabs: List[BrowserTab]
    created_time: float

@dataclass
class PageState:
    url: str
    title: str
    ready_state: str
    loading: bool
    has_dialog: bool
    requires_login: bool
    has_file_chooser: bool

@dataclass
class NavigationResult:
    final_url: str
    page_title: str
    redirected: bool
    load_time_ms: int
    verification_status: str

@dataclass
class BrowserContext:
    session: BrowserSession
    tab: Optional[BrowserTab] = None
    page: Optional[Any] = None
    frame: Optional[Any] = None
    selection: Optional[str] = None
    page_state: Optional[PageState] = None
