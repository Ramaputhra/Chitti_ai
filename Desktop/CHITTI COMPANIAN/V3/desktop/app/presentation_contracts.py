from abc import ABC, abstractmethod
from typing import Dict, Any
from desktop.models.interaction import ExpressionRequested
from desktop.models.presentation import PresentationProfile

class IExpressionRenderer(ABC):
    """
    Renders an abstract ExpressionRequested into a specific format string or object.
    Rule 181: Rendering is Lossless.
    """
    @abstractmethod
    def get_format_name(self) -> str:
        """Returns the format key (e.g., 'text', 'ssml', 'html')."""
        pass
        
    @abstractmethod
    def render(self, request: ExpressionRequested) -> Any:
        """Translates the abstract request into the target format."""
        pass

class DefaultTextRenderer(IExpressionRenderer):
    def get_format_name(self) -> str:
        return "text"
        
    def render(self, request: ExpressionRequested) -> Any:
        # Rule 181: Lossless transformation
        # In a real system, this might add formatting, markdown, etc.
        # For now, it just ensures it's a string.
        payload_str = str(request.payload)
        if request.emotion != "NEUTRAL":
            # Simple text decoration for emotion
            return f"[{request.emotion}] {payload_str}"
        return payload_str

class MarkdownRenderer(IExpressionRenderer):
    def get_format_name(self) -> str:
        return "markdown"
        
    def render(self, request: ExpressionRequested) -> Any:
        return f"**{request.payload}**"
