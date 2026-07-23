from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseRenderer(ABC):
    """
    Interface for rendering Avatar visuals.
    Allows hot-swapping between GIF, MP4, Lottie, or Robot hardware backends.
    """

    @abstractmethod
    def preload(self, profile: Dict[str, Any]) -> None:
        """Load and cache assets from the profile for zero-latency switching."""
        pass

    @abstractmethod
    def play(self, state: str) -> None:
        """Switch to and play the specified visual state."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop current animation."""
        pass

    @abstractmethod
    def pause(self) -> None:
        """Pause current animation."""
        pass

    @abstractmethod
    def resume(self) -> None:
        """Resume current animation."""
        pass

    @abstractmethod
    def current_state(self) -> str:
        """Return the currently playing visual state."""
        pass
