from typing import Optional
from desktop.capabilities.screen_understanding.models import ScreenObservation
from desktop.capabilities.screen_understanding.providers import SemanticObservationProvider

class ObservationFusion:
    """
    Merges OS-native observations into a single fused observation object.
    Prepares the data for the AI Runtime (Rule 129).
    """
    def __init__(self, provider: SemanticObservationProvider):
        self.provider = provider
        
    def fuse(self, include_screenshot: bool = True) -> ScreenObservation:
        screenshot = self.provider.capture_screenshot() if include_screenshot else None
        ui_tree = self.provider.get_ui_tree()
        metadata = self.provider.get_window_metadata()
        clipboard = self.provider.get_clipboard_text()
        
        # In a real implementation, this is where we would align OCR 
        # bounds with UIA bounds to fix missing labels, before hitting the AI.
        
        return ScreenObservation(
            screenshot_path=screenshot,
            ui_tree=ui_tree,
            ocr_text="[Mock OCR Text]",
            window_metadata=metadata,
            clipboard_text=clipboard
        )
