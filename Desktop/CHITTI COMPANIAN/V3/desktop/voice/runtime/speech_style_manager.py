from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class SpeechStyle:
    style_id: str
    name: str
    speed_modifier: float = 1.0
    pitch_modifier: float = 1.0
    pause_modifier: float = 1.0
    energy_level: str = "NORMAL"

class SpeechStyleManager:
    """
    S36A: Speech Style Manager managing 8 canonical speaking styles.
    """
    STYLES: Dict[str, SpeechStyle] = {
        "friendly": SpeechStyle("friendly", "Friendly", 1.05, 1.02, 1.0, "HIGH"),
        "professional": SpeechStyle("professional", "Professional", 1.0, 1.0, 1.1, "NORMAL"),
        "teacher": SpeechStyle("teacher", "Teacher", 0.9, 1.0, 1.3, "EXPLANATORY"),
        "motivational": SpeechStyle("motivational", "Motivational", 1.1, 1.05, 0.9, "ENERGETIC"),
        "minimal": SpeechStyle("minimal", "Minimal", 1.15, 0.98, 0.8, "LOW"),
        "casual": SpeechStyle("casual", "Casual", 1.05, 1.0, 1.0, "RELAXED"),
        "story": SpeechStyle("story", "Story", 0.92, 1.03, 1.4, "EXPRESSIVE"),
        "assistant": SpeechStyle("assistant", "Assistant", 1.02, 1.0, 1.0, "HELPFUL")
    }

    def __init__(self, active_style_id: str = "friendly"):
        self._active_style_id = active_style_id if active_style_id in self.STYLES else "friendly"

    @property
    def active_style(self) -> SpeechStyle:
        return self.STYLES[self._active_style_id]

    def set_active_style(self, style_id: str) -> bool:
        sid = style_id.lower()
        if sid in self.STYLES:
            self._active_style_id = sid
            return True
        return False

    def list_styles(self) -> List[SpeechStyle]:
        return list(self.STYLES.values())
