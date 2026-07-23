from typing import Dict, Any, Optional
from desktop.capabilities.screen_understanding.models import ScreenModel

class IContextExtractor:
    """Plugin interface for extracting domain-specific context."""
    def supports(self, screen_model: ScreenModel) -> bool:
        raise NotImplementedError
        
    def extract(self, screen_model: ScreenModel) -> Dict[str, Any]:
        """Returns semantic context updates (e.g. project root, meeting state)."""
        raise NotImplementedError

class IDEExtractor(IContextExtractor):
    def supports(self, screen_model: ScreenModel) -> bool:
        app = screen_model.application.lower()
        return "code.exe" in app or "pycharm" in app or "idea" in app

    def extract(self, screen_model: ScreenModel) -> Dict[str, Any]:
        # Stub: Spawns subprocess for `git rev-parse --show-toplevel`
        # and `git branch --show-current` in the background.
        return {
            "current_project": {
                "value": "CHITTI",
                "confidence": 0.98,
                "sources": ["IDE", "Git"]
            },
            "coding_context": {
                "value": {"branch": "feature/context", "modified_files": 2},
                "confidence": 0.95,
                "sources": ["Git"]
            }
        }

class BrowserExtractor(IContextExtractor):
    def supports(self, screen_model: ScreenModel) -> bool:
        app = screen_model.application.lower()
        return "chrome" in app or "edge" in app or "firefox" in app

    def extract(self, screen_model: ScreenModel) -> Dict[str, Any]:
        # Stub: Queries browser accessibility APIs to get the current URL
        return {
            "browser_context": {
                "value": {"url": "https://github.com/microsoft/playwright", "domain": "github.com"},
                "confidence": 1.0,
                "sources": ["Accessibility API"]
            }
        }

class MeetingExtractor(IContextExtractor):
    def supports(self, screen_model: ScreenModel) -> bool:
        app = screen_model.application.lower()
        return "zoom" in app or "teams" in app or "meet" in app

    def extract(self, screen_model: ScreenModel) -> Dict[str, Any]:
        return {
            "meeting": {
                "value": {"in_meeting": True, "participants": ["Team"]},
                "confidence": 0.90,
                "sources": ["Window Title", "Process List"]
            }
        }
