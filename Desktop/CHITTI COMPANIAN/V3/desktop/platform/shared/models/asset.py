from dataclasses import dataclass
from typing import Optional


@dataclass
class AIAsset:
    """
    Represents a local AI model asset (Whisper, Piper, Ollama weights, etc).
    """
    id: str
    name: str
    version: str
    path: str
    checksum: str
    is_installed: bool
    is_healthy: bool
    description: Optional[str] = None
