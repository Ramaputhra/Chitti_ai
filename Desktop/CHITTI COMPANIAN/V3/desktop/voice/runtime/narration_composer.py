import re
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class SegmentedNarration:
    raw_text: str
    normalized_text: str
    sentences: List[str] = field(default_factory=list)
    paragraphs: List[str] = field(default_factory=list)
    emotion_tag: str = "NEUTRAL"
    style_tag: str = "FRIENDLY"

class NarrationComposer:
    """
    S36A: Receives LLM text output, normalizes whitespace and punctuation, segments into sentences & paragraphs,
    and tags context, emotion, and speaking style.
    """
    def compose_narration(self, text: str, emotion_hint: str = "NEUTRAL", style_hint: str = "FRIENDLY") -> SegmentedNarration:
        # 1. Normalize whitespace & punctuation
        clean = re.sub(r'\s+', ' ', text).strip()
        clean = clean.replace("..", ".").replace("!!", "!")

        # 2. Paragraph segmentation
        paragraphs = [p.strip() for p in clean.split("\n") if p.strip()]
        if not paragraphs:
            paragraphs = [clean]

        # 3. Sentence segmentation
        sentences = [s.strip() + "." for s in re.split(r'[.!?]+', clean) if s.strip()]

        return SegmentedNarration(
            raw_text=text,
            normalized_text=clean,
            sentences=sentences,
            paragraphs=paragraphs,
            emotion_tag=emotion_hint.upper(),
            style_tag=style_hint.upper()
        )
