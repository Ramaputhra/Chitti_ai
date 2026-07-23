import os
import glob
from typing import Any, Dict

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.document_provider import IDocumentProvider
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.artifact import DocumentArtifact


class LocalDocumentProvider(IDocumentProvider):
    """
    Mock local document provider that just scans recent text files for V0.1.
    """
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED
        self.docs_dir = os.path.expanduser("~/CHITTI_Workspace/Documents")

    @property
    def name(self) -> str:
        return "LocalDocumentProvider"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        if not os.path.exists(self.docs_dir):
            try:
                os.makedirs(self.docs_dir, exist_ok=True)
                self.logger.info(f"Created default documents directory at {self.docs_dir}")
            except Exception as e:
                self.logger.warning(f"Failed to create documents directory: {e}")
                self._state = ServiceState.ERROR
                return
                
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {"docs_dir_exists": os.path.exists(self.docs_dir)}

    def read_document(self, path: str) -> DocumentArtifact:
        if self._state != ServiceState.RUNNING:
            raise RuntimeError("Provider is not running.")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return DocumentArtifact(
            source=self.name,
            capability="DocumentsCapability",
            metadata={"path": path},
            content=content
        )

    def summarize_document(self, path: str) -> DocumentArtifact:
        raise NotImplementedError("Summarize document not implemented.")
