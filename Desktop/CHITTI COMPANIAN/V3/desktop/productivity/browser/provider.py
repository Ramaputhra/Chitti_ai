from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from desktop.models.browser import BrowserTab

class BrowserProvider(ABC):
    """
    Interface for extracting browser history from a local browser instance (e.g., via SQLite).
    """
    
    @property
    @abstractmethod
    def browser_name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def executable_names(self) -> List[str]:
        """e.g., ['chrome.exe']"""
        pass
        
    @abstractmethod
    def extract_recent_history(self, since_timestamp: float) -> List[BrowserTab]:
        """
        Extract recent history from the local database securely.
        Must gracefully fail if the database cannot be read.
        """
        pass
