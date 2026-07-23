from abc import ABC, abstractmethod
from typing import Any, Dict, List

class IWidgetRenderer(ABC):
    """
    Standard backend Widget contract.
    """
    
    @abstractmethod
    def render(self, context: Any) -> Dict[str, Any]:
        """Generates the initial WidgetDescriptor/data model."""
        pass

    @abstractmethod
    def refresh(self, context: Any) -> Dict[str, Any]:
        """Generates a patch/diff to update an existing widget."""
        pass

    @abstractmethod
    def serialize(self) -> str:
        pass

    @abstractmethod
    def deserialize(self, data: str) -> None:
        pass

    @abstractmethod
    def supports_action(self, action_id: str) -> bool:
        """e.g. returns True for 'copy', 'pin', 'drill_down'"""
        pass

    @abstractmethod
    def validate(self) -> bool:
        pass

    @abstractmethod
    def dispose(self) -> None:
        pass
