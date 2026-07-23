from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class BrowserProfile:
    preferred_search_provider: str = "google"
    reader_mode: bool = False
    download_directory: str = ""
    javascript_enabled: bool = True
    private_mode: bool = False
    timeout_policy: str = "standard"
    popup_policy: str = "block"
    cookie_policy: str = "reject_third_party"

@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)

@dataclass
class SearchDataset:
    """Generic dataset usable by any search provider, not just browser."""
    query: str
    results: List[SearchResult] = field(default_factory=list)

@dataclass
class ArticleContent:
    title: str
    author: Optional[str]
    published_date: Optional[str]
    body_text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PageContent:
    url: str
    title: str
    text_content: str

@dataclass
class TableContent:
    headers: List[str]
    rows: List[List[str]]

@dataclass
class FormContent:
    form_id: str
    fields: List[Dict[str, Any]]

@dataclass
class LinkCollection:
    links: List[Dict[str, str]]

@dataclass
class ImageCollection:
    images: List[Dict[str, str]]

@dataclass
class DownloadItem:
    filename: str
    size_bytes: int
    status: str
    url: str
