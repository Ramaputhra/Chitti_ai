import logging
from typing import Dict, Any, Optional
from desktop.shared.motion.motion_tokens import SPRING_WIDGET, SPRING_DOCK, TimingToken
from desktop.shared.motion.motion_curves import MotionCurves

logger = logging.getLogger(__name__)

class MotionRuntimeAdapter:
    """
    S36D-1: Motion Runtime Adapter consuming ONLY Motion Tokens from 'desktop/shared/motion/'.
    No local motion constants or local easing curves permitted.
    """
    def __init__(self):
        self.widget_spring = SPRING_WIDGET
        self.dock_spring = SPRING_DOCK
        self.fast_timing_ms = TimingToken.FAST.value
        self.normal_timing_ms = TimingToken.NORMAL.value

    def evaluate_motion_curve(self, curve_name: str, progress: float) -> float:
        curve = MotionCurves.CURVES.get(curve_name, MotionCurves.linear)
        return curve(progress)
