from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(frozen=True)
class ResponsePacket:
    text: str
    emotion: str
    animation: str
    audio_metadata: Dict[str, Any] = field(default_factory=dict)
    ui_metadata: Dict[str, Any] = field(default_factory=dict)
    timing_metadata: Dict[str, Any] = field(default_factory=dict)
