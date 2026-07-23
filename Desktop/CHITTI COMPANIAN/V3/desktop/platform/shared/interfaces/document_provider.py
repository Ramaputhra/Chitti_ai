from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.artifact import DocumentArtifact


class IDocumentProvider(IService):
    """
    Abstracts specific file format parsers (PDF, DOCX, etc) for the DocumentsCapability.
    """
    def read_document(self, path: str) -> DocumentArtifact:
        ...

    def summarize_document(self, path: str) -> DocumentArtifact:
        ...
