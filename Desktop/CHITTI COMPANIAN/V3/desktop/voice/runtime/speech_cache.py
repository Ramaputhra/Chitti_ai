import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from desktop.character.behavior.speech.speech_context import SpeechTimeline

@dataclass
class CachedSpeechEntry:
    speech_id: str
    text_narration: str
    audio_path: str
    timeline: SpeechTimeline
    created_at: float
    access_count: int = 1

class SpeechCache:
    """
    S36A: Caches synthesized audio and SpeechTimeline metadata for repeated speech responses.
    """
    def __init__(self, max_entries: int = 100):
        self._cache: Dict[str, CachedSpeechEntry] = {}
        self.max_entries = max_entries

    def get(self, text_narration: str, voice_profile: str) -> Optional[Tuple[str, SpeechTimeline]]:
        key = f"{voice_profile}:{text_narration.strip().lower()}"
        entry = self._cache.get(key)
        if entry:
            entry.access_count += 1
            return entry.audio_path, entry.timeline
        return None

    def put(self, text_narration: str, voice_profile: str, speech_id: str, audio_path: str, timeline: SpeechTimeline):
        if len(self._cache) >= self.max_entries:
            # Evict oldest entry
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].created_at)
            del self._cache[oldest_key]

        key = f"{voice_profile}:{text_narration.strip().lower()}"
        self._cache[key] = CachedSpeechEntry(
            speech_id=speech_id,
            text_narration=text_narration,
            audio_path=audio_path,
            timeline=timeline,
            created_at=time.time()
        )

    def clear(self):
        self._cache.clear()

    @property
    def size(self) -> int:
        return len(self._cache)
