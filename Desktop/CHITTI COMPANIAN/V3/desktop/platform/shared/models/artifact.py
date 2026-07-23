import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from desktop.platform.shared.models.provenance import Provenance


@dataclass
class Artifact:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "Artifact"
    source: str = "Unknown"
    created_at: float = field(default_factory=time.time)
    session_id: Optional[str] = None
    capability: Optional[str] = None
    provenance: Optional[Provenance] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    content: Any = None


@dataclass
class DocumentArtifact(Artifact): type: str = "DocumentArtifact"

@dataclass
class EmailArtifact(Artifact): type: str = "EmailArtifact"

@dataclass
class CalendarArtifact(Artifact): type: str = "CalendarArtifact"

@dataclass
class ContactArtifact(Artifact): type: str = "ContactArtifact"

@dataclass
class ImageArtifact(Artifact): type: str = "ImageArtifact"

@dataclass
class AudioArtifact(Artifact): type: str = "AudioArtifact"

@dataclass
class VideoArtifact(Artifact): type: str = "VideoArtifact"

@dataclass
class WebPageArtifact(Artifact): type: str = "WebPageArtifact"

@dataclass
class SearchResultArtifact(Artifact): type: str = "SearchResultArtifact"

@dataclass
class TaskArtifact(Artifact): type: str = "TaskArtifact"

@dataclass
class SummaryArtifact(Artifact): type: str = "SummaryArtifact"
