from dataclasses import dataclass
from enum import Enum

class TimingToken(Enum):
    FAST = 120        # ms
    NORMAL = 180      # ms
    MEDIUM = 240      # ms
    SLOW = 320        # ms
    LONG = 450        # ms
    BREATH = 3000     # ms
    IDLE = 5000       # ms
    SLEEP = 8000      # ms

class OpacityToken(Enum):
    INVISIBLE = 0.0
    HIDDEN = 0.0
    SUBTLE = 0.3
    HOVER = 0.8
    FOCUSED = 0.9
    ACTIVE = 1.0
    NOTIFICATION = 0.95
    TOOLTIP = 0.92

class ScaleToken(Enum):
    NORMAL = 1.0
    HOVER = 1.03
    PRESSED = 0.97
    EXPANDED = 1.05
    DOCKED = 0.95
    SLIME_STRETCH = 1.05    # Max 5% stretch
    SLIME_COMPRESS = 0.96   # Max 4% compression

@dataclass
class SpringToken:
    name: str
    stiffness: float
    damping: float
    mass: float = 1.0
    overshoot: float = 0.0
    settling_time_ms: float = 240.0

# Canonical Spring Tokens
SPRING_WAKE = SpringToken("SPRING_WAKE", stiffness=180.0, damping=18.0, mass=1.0, overshoot=0.04, settling_time_ms=300.0)
SPRING_DOCK = SpringToken("SPRING_DOCK", stiffness=220.0, damping=22.0, mass=1.0, overshoot=0.02, settling_time_ms=250.0)
SPRING_SLIME = SpringToken("SPRING_SLIME", stiffness=140.0, damping=12.0, mass=0.9, overshoot=0.05, settling_time_ms=320.0)
SPRING_WIDGET = SpringToken("SPRING_WIDGET", stiffness=200.0, damping=20.0, mass=1.0, overshoot=0.03, settling_time_ms=220.0)
SPRING_TOOLTIP = SpringToken("SPRING_TOOLTIP", stiffness=260.0, damping=24.0, mass=0.8, overshoot=0.01, settling_time_ms=180.0)
SPRING_DIALOG = SpringToken("SPRING_DIALOG", stiffness=190.0, damping=19.0, mass=1.0, overshoot=0.02, settling_time_ms=280.0)
SPRING_NOTIFICATION = SpringToken("SPRING_NOTIFICATION", stiffness=210.0, damping=20.0, mass=1.0, overshoot=0.03, settling_time_ms=240.0)
SPRING_PANEL = SpringToken("SPRING_PANEL", stiffness=170.0, damping=18.0, mass=1.1, overshoot=0.01, settling_time_ms=300.0)
SPRING_CHARACTER = SpringToken("SPRING_CHARACTER", stiffness=160.0, damping=16.0, mass=1.0, overshoot=0.04, settling_time_ms=320.0)
SPRING_PRESENTATION = SpringToken("SPRING_PRESENTATION", stiffness=150.0, damping=17.0, mass=1.1, overshoot=0.01, settling_time_ms=350.0)
SPRING_EXPAND = SpringToken("SPRING_EXPAND", stiffness=190.0, damping=18.0, mass=1.0, overshoot=0.03, settling_time_ms=260.0)
SPRING_COLLAPSE = SpringToken("SPRING_COLLAPSE", stiffness=230.0, damping=22.0, mass=1.0, overshoot=0.01, settling_time_ms=200.0)
SPRING_BOUNCE = SpringToken("SPRING_BOUNCE", stiffness=150.0, damping=10.0, mass=0.9, overshoot=0.08, settling_time_ms=380.0)
SPRING_IDLE = SpringToken("SPRING_IDLE", stiffness=80.0, damping=14.0, mass=1.2, overshoot=0.0, settling_time_ms=500.0)
SPRING_BREATH = SpringToken("SPRING_BREATH", stiffness=40.0, damping=10.0, mass=1.5, overshoot=0.0, settling_time_ms=3000.0)
SPRING_TOOLTIP_SHOW = SpringToken("SPRING_TOOLTIP_SHOW", stiffness=250.0, damping=22.0, mass=0.8, overshoot=0.02, settling_time_ms=160.0)
SPRING_TOOLTIP_HIDE = SpringToken("SPRING_TOOLTIP_HIDE", stiffness=280.0, damping=26.0, mass=0.8, overshoot=0.0, settling_time_ms=140.0)
