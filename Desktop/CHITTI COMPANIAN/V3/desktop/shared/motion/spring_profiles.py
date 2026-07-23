from typing import Dict
from desktop.shared.motion.motion_tokens import (
    SpringToken, SPRING_WAKE, SPRING_DOCK, SPRING_SLIME, SPRING_WIDGET,
    SPRING_TOOLTIP, SPRING_CHARACTER, SPRING_BOUNCE, SPRING_BREATH
)

class SpringProfiles:
    """
    S36E: Reusable Spring Presets definitions.
    Inspired by Apple HIG and Windows 11 Fluent Motion physics.
    """
    GENTLE = SpringToken("Gentle", stiffness=120.0, damping=16.0, mass=1.0, overshoot=0.01, settling_time_ms=350.0)
    RESPONSIVE = SpringToken("Responsive", stiffness=240.0, damping=24.0, mass=0.9, overshoot=0.01, settling_time_ms=180.0)
    PLAYFUL = SpringToken("Playful", stiffness=160.0, damping=11.0, mass=0.8, overshoot=0.06, settling_time_ms=320.0)
    HEAVY = SpringToken("Heavy", stiffness=140.0, damping=20.0, mass=1.4, overshoot=0.0, settling_time_ms=400.0)
    ELASTIC = SpringToken("Elastic", stiffness=130.0, damping=9.0, mass=0.8, overshoot=0.09, settling_time_ms=420.0)
    DOCK = SPRING_DOCK
    SLIME = SPRING_SLIME
    WAKE = SPRING_WAKE
    TOOLTIP = SPRING_TOOLTIP
    WIDGET = SPRING_WIDGET
    CHARACTER = SPRING_CHARACTER

    PROFILES: Dict[str, SpringToken] = {
        "Gentle": GENTLE,
        "Responsive": RESPONSIVE,
        "Playful": PLAYFUL,
        "Heavy": HEAVY,
        "Elastic": ELASTIC,
        "Dock": DOCK,
        "Slime": SLIME,
        "Wake": WAKE,
        "Tooltip": TOOLTIP,
        "Widget": WIDGET,
        "Character": CHARACTER
    }
