import time
from typing import List, Tuple, Optional
from desktop.character.behavior.speech.speech_context import SpeechTimeline
from desktop.voice.runtime.emotion_markup_engine import SpeechMarkupMetadata

class SpeechTimelineBuilder:
    """
    S36A: Constructs a canonical SpeechTimeline instance for Voice Runtime and Character Runtime integration.
    """
    def build_timeline(
        self,
        speech_id: str,
        audio_id: str,
        duration: float,
        language: str = "en-US",
        voice_profile: str = "friendly_female",
        style: str = "Friendly",
        markup: Optional[SpeechMarkupMetadata] = None,
        provider: str = "SherpaONNX",
        audio_path: Optional[str] = None
    ) -> SpeechTimeline:
        sentences: List[Tuple[float, float]] = []
        phrases: List[Tuple[float, float]] = []
        pauses: List[float] = markup.pause_points if markup else [duration * 0.5]
        emphasis: List[float] = markup.emphasis_points if markup else []
        speed: float = markup.speed_rate if markup else 1.0

        # Construct sentence boundaries
        num_sentences = max(1, len(pauses) + 1)
        seg_dur = duration / num_sentences
        for i in range(num_sentences):
            start = i * seg_dur
            end = min(duration, (i + 1) * seg_dur)
            sentences.append((round(start, 2), round(end, 2)))
            phrases.append((round(start, 2), round(start + seg_dur * 0.5, 2)))

        return SpeechTimeline(
            speech_id=speech_id,
            audio_id=audio_id,
            total_duration=round(duration, 2),
            speech_rate=speed,
            language=language,
            voice=voice_profile,
            start_time=0.0,
            estimated_end_time=round(duration, 2),
            sentence_boundaries=sentences,
            phrase_boundaries=phrases,
            pause_points=pauses,
            emphasis_points=emphasis,
            tts_provider=provider,
            metadata={"style": style, "audio_path": audio_path}
        )
