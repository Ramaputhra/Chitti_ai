from abc import ABC, abstractmethod
from desktop.models.documents import DocumentContent
import os

class DocumentParser(ABC):
    @abstractmethod
    def extract(self, file_path: str) -> DocumentContent:
        pass

class MarkItDownParser(DocumentParser):
    """
    MVP Implementation representing a unified markdown extraction layer.
    Abstracted so CHITTI doesn't tightly couple to the actual library (e.g. microsoft/markitdown).
    """
    def extract(self, file_path: str) -> DocumentContent:
        # In a real environment, we would do:
        # from markitdown import MarkItDown
        # md = MarkItDown()
        # result = md.convert(file_path)
        # return DocumentContent(markdown=result.text_content)
        
        # For this MVP stub, we simulate extraction.
        content = DocumentContent()
        filename = os.path.basename(file_path).lower()
        
        content.metadata = {
            "source": file_path,
            "filename": filename
        }
        
        if filename.endswith(".pdf"):
            content.markdown = f"# PDF Document\nExtracted content from {filename}."
            content.page_count = 5
        elif filename.endswith(".docx"):
            content.markdown = f"# Word Document\nHeading 1\nThis is a screenplay docx."
            content.sections = ["Heading 1"]
        elif filename.endswith(".xlsx") or filename.endswith(".csv"):
            content.markdown = f"# Spreadsheet\n| Item | Cost |\n|---|---|\n| Total Budget | $50,000 |"
            content.tables = ["| Item | Cost |\n|---|---|\n| Total Budget | $50,000 |"]
        else:
            content.markdown = f"Extracted text for {filename}."
            
        return content
