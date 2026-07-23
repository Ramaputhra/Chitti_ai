from typing import Optional
from desktop.capabilities.screen_understanding.models import ScreenModel, ScreenDiff

class EpisodeDetector:
    """
    Filters high-frequency screen updates to decide what gets 
    persisted into the Memory Runtime as a discrete 'Episode'.
    """
    def __init__(self):
        self.previous_model: Optional[ScreenModel] = None

    def evaluate_change(self, current_model: ScreenModel) -> tuple[bool, Optional[ScreenDiff]]:
        """
        Returns (is_meaningful, diff)
        """
        if not self.previous_model:
            self.previous_model = current_model
            return True, None
            
        # Stub logic: Check if application or intent changed
        app_changed = current_model.application != self.previous_model.application
        intent_changed = current_model.current_intent != self.previous_model.current_intent
        
        # Minimal changes like typing a single char shouldn't trigger
        # We assume `current_model` has a hash or control count we can diff
        
        is_meaningful = app_changed or intent_changed
        
        diff = None
        if is_meaningful:
            diff = ScreenDiff(
                previous_timestamp=self.previous_model.timestamp,
                current_timestamp=current_model.timestamp,
                added_elements=[],
                removed_elements=[],
                intent_changed=intent_changed,
                summary_of_change="User switched from browsing to coding." if intent_changed else "Application state evolved."
            )
            
        self.previous_model = current_model
        return is_meaningful, diff
