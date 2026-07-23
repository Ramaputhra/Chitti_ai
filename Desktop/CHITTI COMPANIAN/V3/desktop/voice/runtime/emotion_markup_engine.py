from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any

@dataclass
class SpeechMarkupMetadata:
    pause_points: List[float] = field(default_factory=list)
    emphasis_points: List[float] = field(default_factory=list)
    speed_rate: float = 1.0
    pitch_modifier: float = 1.0
    volume_modifier: float = 1.0
    expression_tags: List[str] = field(default_factory=list)

class EmotionMarkupEngine:
    """
    S36A: Generates provider-independent speech markup metadata (pause, emphasis, slow, fast, soft, strong, question, warning, celebration).
    Does NOT generate provider-specific SSML strings.
    """
    def process_markup(self, text: str, emotion_tag: str = "NEUTRAL", duration_est: float = 5.0) -> SpeechMarkupMetadata:
        pauses = []
        emphasis = []
        speed = 1.0
        pitch = 1.0
        vol = 1.0
        tags = [emotion_tag.upper()]

        # Generate pause points on commas and sentence breaks
        words = text.split()
        total_words = len(words) if words else 1
        
        for i, word in enumerate(words):
            rel_time = (i / total_words) * duration_est
            if "," in word or "." in word or "!" in word or "?" in word:
                pauses.append(round(rel_time, 2))
            if word.isupper() and len(word) > 1:
                emphasis.append(round(rel_time, 2))

        tag_u = emotion_tag.upper()
        if tag_u in ("HAPPY", "CELEBRATION"):
            speed = 1.08
            pitch = 1.05
            tags.append("celebration")
        elif tag_u in ("WARNING", "ALERT"):
            speed = 0.95
            vol = 1.1
            tags.append("warning")
        elif tag_u in ("QUESTION", "CONFUSED"):
            pitch = 1.08
            tags.append("question")

        return SpeechMarkupMetadata(
            pause_points=pauses,
            emphasis_points=emphasis,
            speed_rate=speed,
            pitch_modifier=pitch,
            volume_modifier=vol,
            expression_tags=tags
        )
