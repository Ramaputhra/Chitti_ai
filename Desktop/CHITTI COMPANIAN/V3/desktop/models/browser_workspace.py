from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass(frozen=True)
class KnowledgeEntity:
    title: str
    content_snippet: str
    code_blocks: List[str] = field(default_factory=list)
    source_url: str = ""

@dataclass(frozen=True)
class CommerceEntity:
    product_name: str
    price: str
    currency: str
    stock_status: str
    rating: float = 0.0
    source_url: str = ""

@dataclass(frozen=True)
class BrowserWorkspaceSummary:
    workspace_name: str
    intent: str
    active_artifacts: List[str]
    last_active: datetime
    summary: str

@dataclass(frozen=True)
class BrowserWorkspace:
    workspace_id: str
    workspace_name: str
    intent: str
    artifacts: List[Any] = field(default_factory=list)
    last_active: datetime = field(default_factory=datetime.now)
    
    def to_summary(self) -> BrowserWorkspaceSummary:
        return BrowserWorkspaceSummary(
            workspace_name=self.workspace_name,
            intent=self.intent,
            active_artifacts=[a.artifact_type for a in self.artifacts],
            last_active=self.last_active,
            summary=f"{self.workspace_name} with {len(self.artifacts)} active artifacts."
        )
