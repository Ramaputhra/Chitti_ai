from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional, Any
from desktop.models.evidence import EvidenceCluster

@dataclass
class BrowserTab:
    url: str
    title: str
    domain: str
    opened_at: float
    closed_at: Optional[float] = None
    reading_duration: float = 0.0

@dataclass
class DomainCluster(EvidenceCluster):
    primary_tab: Optional[BrowserTab] = None

@dataclass
class BrowserContext:
    browser: str
    tabs: List[BrowserTab] = field(default_factory=list)
    active_tab: Optional[BrowserTab] = None
    domains: Set[str] = field(default_factory=set)
    total_reading_time: float = 0.0
    domain_clusters: Dict[str, DomainCluster] = field(default_factory=dict)
    # DuplicateGroups is removed since it's now RedundantEvidence returned by the Provider
    total_tabs: int = 0
    unique_tabs: int = 0

@dataclass
class BrowserSessionSnapshot:
    browser: str
    urls: List[str]
    active_url: Optional[str] = None
