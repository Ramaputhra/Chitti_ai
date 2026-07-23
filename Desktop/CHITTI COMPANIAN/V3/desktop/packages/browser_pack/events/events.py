from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class BrowserEvent:
    event_type: str
    target_uri: str
    metadata: Dict[str, Any]

class SearchCompleted(BrowserEvent):
    def __init__(self, query: str, result_count: int):
        super().__init__("SearchCompleted", "", {"query": query, "result_count": result_count})

class PageRead(BrowserEvent):
    def __init__(self, url: str):
        super().__init__("PageRead", url, {})

class ArticleExtracted(BrowserEvent):
    def __init__(self, url: str, title: str):
        super().__init__("ArticleExtracted", url, {"title": title})

class DownloadStarted(BrowserEvent):
    def __init__(self, url: str, filename: str):
        super().__init__("DownloadStarted", url, {"filename": filename})

class DownloadCompleted(BrowserEvent):
    def __init__(self, url: str, filename: str, success: bool):
        super().__init__("DownloadCompleted", url, {"filename": filename, "success": success})

class FormSubmitted(BrowserEvent):
    def __init__(self, url: str, form_id: str):
        super().__init__("FormSubmitted", url, {"form_id": form_id})

class NavigationCompleted(BrowserEvent):
    def __init__(self, url: str, status_code: int):
        super().__init__("NavigationCompleted", url, {"status_code": status_code})
