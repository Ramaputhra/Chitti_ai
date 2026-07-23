from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.artifact import DocumentArtifact
from typing import List


class INotesProvider(IService):
    """
    Abstracts specific note taking backends (Evernote, Notion, Local Markdown, Apple Notes)
    for the NotesCapability.
    """
    def query_notes(self, query: str) -> List[DocumentArtifact]:
        ...

    def create_note(self, title: str, content: str) -> DocumentArtifact:
        ...
