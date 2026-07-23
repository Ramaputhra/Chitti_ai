import os
from typing import Any, Dict, List

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.notes_provider import INotesProvider
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.artifact import DocumentArtifact


class LocalNotesProvider(INotesProvider):
    """
    Scans a designated local directory for .txt or .md files to gather meeting notes.
    """
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED
        self.notes_dir = os.path.expanduser("~/CHITTI_Workspace/Notes")

    @property
    def name(self) -> str:
        return "LocalNotesProvider"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        if not os.path.exists(self.notes_dir):
            try:
                os.makedirs(self.notes_dir, exist_ok=True)
                self.logger.info(f"Created default notes directory at {self.notes_dir}")
            except Exception as e:
                self.logger.warning(f"Failed to create notes directory: {e}")
                self._state = ServiceState.ERROR
                return
                
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {"notes_dir_exists": os.path.exists(self.notes_dir)}

    def query_notes(self, query: str) -> List[DocumentArtifact]:
        if self._state != ServiceState.RUNNING:
            return []
            
        artifacts = []
        try:
            for filename in os.listdir(self.notes_dir):
                if filename.endswith(".md") or filename.endswith(".txt"):
                    filepath = os.path.join(self.notes_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Very simple mock matching: if query is in filename or content
                    if query.lower() in filename.lower() or query.lower() in content.lower():
                        artifacts.append(
                            DocumentArtifact(
                                source=self.name,
                                capability="NotesCapability",
                                metadata={"title": filename, "path": filepath},
                                content=content
                            )
                        )
        except Exception as e:
            self.logger.warning(f"Error querying local notes: {e}")
            
        return artifacts

    def create_note(self, title: str, content: str) -> DocumentArtifact:
        raise NotImplementedError("Local note creation not yet implemented.")
