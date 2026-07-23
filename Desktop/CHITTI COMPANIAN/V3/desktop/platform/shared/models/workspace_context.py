from dataclasses import dataclass, field
from typing import List

from desktop.platform.shared.models.artifact import Artifact, DocumentArtifact


@dataclass
class WorkspaceContext:
    """
    Unified context object consolidating all capability streams.
    """
    calendar_events: List[Artifact] = field(default_factory=list)
    unread_emails: List[Artifact] = field(default_factory=list)
    desktop_state: List[DocumentArtifact] = field(default_factory=list)
    meeting_notes: List[DocumentArtifact] = field(default_factory=list)
    recent_documents: List[DocumentArtifact] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (
            self.calendar_events or
            self.unread_emails or
            self.desktop_state or
            self.meeting_notes or
            self.recent_documents
        )
