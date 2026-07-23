from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional

@dataclass
class SpeechTimeline:
    """
    S34B-R1: Single canonical SpeechTimeline interface between TTS and Behavior Scheduler.
    Contains ZERO phoneme or lip sync data.
    """
    speech_id: str
    audio_id: str
    total_duration: float
    speech_rate: float = 1.0
    language: str = "en-US"
    voice: str = "chitti_voice_v1"
    start_time: float = 0.0
    estimated_end_time: float = 0.0
    sentence_boundaries: List[Tuple[float, float]] = field(default_factory=list)
    phrase_boundaries: List[Tuple[float, float]] = field(default_factory=list)
    pause_points: List[float] = field(default_factory=list)
    emphasis_points: List[float] = field(default_factory=list)
    tts_provider: str = "MockTTSProvider"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.estimated_end_time <= 0.0:
            self.estimated_end_time = self.start_time + self.total_duration

@dataclass
class SpeechContext:
    """
    S34B-R1: Speech Context wrapping SpeechTimeline for scheduler processing.
    """
    timeline: SpeechTimeline
    text_narration: str = ""
    is_speaking: bool = False

@dataclass
class MockSpeechTimeline:
    """
    S34B-R1: Mock Speech Timeline generator for behavior simulation.
    """
    @staticmethod
    def create_mock_speech(speech_id: str, duration: float = 6.0) -> SpeechContext:
        bounds = [
            (0.0, duration * 0.4),
            (duration * 0.45, duration * 0.85),
            (duration * 0.9, duration)
        ]
        phrases = [
            (0.0, duration * 0.2),
            (duration * 0.2, duration * 0.4),
            (duration * 0.45, duration * 0.65),
            (duration * 0.65, duration * 0.85)
        ]
        pauses = [duration * 0.4, duration * 0.85]
        emphasis = [duration * 0.2, duration * 0.65]

        st = SpeechTimeline(
            speech_id=speech_id,
            audio_id=f"audio_{speech_id}",
            total_duration=duration,
            sentence_boundaries=bounds,
            phrase_boundaries=phrases,
            pause_points=pauses,
            emphasis_points=emphasis
        )
        return SpeechContext(
            timeline=st,
            text_narration="Mock presentation speech narration sample for simulation.",
            is_speaking=True
        )
