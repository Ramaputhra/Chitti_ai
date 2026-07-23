from typing import Any, Dict

from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.screen_model import ScreenModel


class IScreenProvider(IService):
    """
    Standard interface for Screen Runtime capabilities.
    Each provider analyzes the raw frame and enriches the unified `ScreenModel`
    in place, rather than dumping standalone artifacts prematurely.
    """
    def analyze(self, raw_frame: bytes, model: ScreenModel) -> None:
        """Processes the frame and mutates the ScreenModel with its findings."""
        ...

    def describe(self) -> Dict[str, Any]:
        """Returns metadata about the provider's capabilities."""
        ...
