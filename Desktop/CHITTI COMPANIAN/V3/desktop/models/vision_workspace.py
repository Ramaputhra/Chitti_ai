from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from desktop.models.browser_workspace import KnowledgeEntity
from datetime import datetime

@dataclass
class VisualBoundingBox:
    x: int
    y: int
    w: int
    h: int

@dataclass
class VisionLayoutTree:
    """Analogous to HTML LayoutTree, structurally maps raw pixels into semantic hierarchy."""
    id: str
    element_type: str
    bounding_box: VisualBoundingBox
    attributes: Dict[str, Any] = field(default_factory=dict)
    children: List['VisionLayoutTree'] = field(default_factory=list)

@dataclass
class VisionWorkspaceSummary:
    """Authoritative conversational context representing visual state."""
    workspace_id: str
    title: str
    active_artifacts: List[str]
    intent_hints: List[str]

@dataclass
class VisionWorkspace:
    """Authoritative execution context representing the user's logical vision session."""
    workspace_id: str
    title: str
    layout_trees: List[VisionLayoutTree] = field(default_factory=list)
    artifacts: List[Any] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def to_summary(self) -> VisionWorkspaceSummary:
        return VisionWorkspaceSummary(
            workspace_id=self.workspace_id,
            title=self.title,
            active_artifacts=[a.artifact_type for a in self.artifacts],
            intent_hints=["Explain Error", "Extract Table", "Summarize Document"]
        )
