from dataclasses import dataclass


@dataclass(frozen=True)
class AudioPacket:
    """
    Standardized payload for audio chunks traveling through the system.
    Eliminates ambiguity around raw bytes.
    """
    timestamp: float
    sample_rate: int
    channels: int
    bit_depth: int
    frame_count: int
    duration: float
    data: bytes

@dataclass(frozen=True)
class TranscriptionResult:
    """Result of speech recognition."""
    text: str
    language: str
    confidence: float
