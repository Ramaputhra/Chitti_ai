from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseProvider(ABC):
    """
    Abstract Base Class for all AI Providers in CHITTI V2.
    """
    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique identifier (e.g., 'liteocr', 'easyocr')."""
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """Provider category (e.g., 'ocr', 'stt', 'tts', 'vision', 'llm')."""
        pass

    @property
    def version(self) -> str:
        """Provider implementation version."""
        return "1.0.0"

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Returns health status dict.
        Must include 'healthy': bool, 'status_code': int, and diagnostic metadata.
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Returns metadata regarding capabilities, model versions, and hardware support."""
        return {
            "provider_id": self.provider_id,
            "category": self.category,
            "version": self.version,
            "supports_cpu": True,
            "supports_gpu": False
        }
