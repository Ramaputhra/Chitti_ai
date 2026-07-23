import os
import glob
from typing import Any, Dict, List

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.document_provider import IDocumentProvider
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.artifact import DocumentArtifact
from desktop.platform.shared.models.capability import CapabilityDescriptor


class DocumentsCapability(ICapability):
    """
    Provides document operations abstracting away the specific IDocumentProvider.
    """
    def __init__(self, logger: ILoggingService, provider: IDocumentProvider) -> None:
        self.logger = logger
        self.providers = [provider]
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "DocumentsCapability"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {
            "active_providers": [p.name for p in self.providers if p.state == ServiceState.RUNNING]
        }

    def execute(self, action: str, parameters: Dict[str, Any]) -> Any:
        if action == "recent":
            return self.get_recent_documents()
        raise NotImplementedError(f"Action {action} not supported by {self.name}")

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name=self.name,
            description="Access and manage user documents.",
            actions=["recent", "read"],
        )

    def get_recent_documents(self) -> List[DocumentArtifact]:
        """Returns metadata about recent documents."""
        results = []
        for provider in self.providers:
            if provider.state == ServiceState.RUNNING:
                try:
                    if hasattr(provider, 'docs_dir'):
                        docs_dir = provider.docs_dir
                        if os.path.exists(docs_dir):
                            files = glob.glob(os.path.join(docs_dir, "*.txt")) + glob.glob(os.path.join(docs_dir, "*.md"))
                            # Sort by modified time
                            files.sort(key=os.path.getmtime, reverse=True)
                            for f in files[:3]:
                                results.append(
                                    DocumentArtifact(
                                        source=provider.name,
                                        capability="DocumentsCapability",
                                        metadata={"path": f, "title": os.path.basename(f)},
                                        content=f"Recent document: {os.path.basename(f)}"
                                    )
                                )
                except Exception as e:
                    self.logger.warning(f"{provider.name} failed to get recent documents: {e}")
        return results
