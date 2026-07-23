from enum import Enum
from dataclasses import dataclass
from typing import Optional

class AnimationLayer(Enum):
    BASE = "BASE"          # Looping core emotion (e.g. Thinking)
    FACE = "FACE"          # Transient overlays (e.g. Blink, Smile)
    GESTURE = "GESTURE"    # Body/head motions (e.g. Nod, Wave)
    LIP_SYNC = "LIP_SYNC"  # Managed exclusively by TTS

class AnimationInterruptLevel(Enum):
    NONE = 0
    SOFT = 1
    NORMAL = 2
    HARD = 3
    CRITICAL = 4

class AnimationPolicy(Enum):
    STACKABLE = "STACKABLE"
    REPLACE = "REPLACE"
    QUEUE = "QUEUE"
    IGNORE_IF_ACTIVE = "IGNORE_IF_ACTIVE"
    COOLDOWN = "COOLDOWN"

class EmotionAnimation(Enum):
    IDLE = "IDLE"
    THINKING = "THINKING"
    FOCUSED = "FOCUSED"
    WAITING = "WAITING"
    HAPPY = "HAPPY"
    SAD = "SAD"

class GestureAnimation(Enum):
    WAVE = "WAVE"
    NOD = "NOD"
    NAMASTE = "NAMASTE"
    POINT = "POINT"
    SHAKE_HEAD = "SHAKE_HEAD"

class FaceAnimation(Enum):
    SMILE = "SMILE"
    BLINK = "BLINK"
    WINK = "WINK"
    EYEBROW_RAISE = "EYEBROW_RAISE"

@dataclass(frozen=True)
class AnimationDescriptor:
    id: str  # Enum string value
    layer: AnimationLayer
    priority: AnimationInterruptLevel
    policy: AnimationPolicy
    loop: bool
    duration_ms: Optional[float] = None
