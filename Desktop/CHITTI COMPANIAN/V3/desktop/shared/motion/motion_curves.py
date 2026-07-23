import math
from typing import Callable, Dict

class MotionCurves:
    """
    S36E: Canonical Easing & Motion Curves for CHITTI Platform.
    No runtime SHALL define custom easing curves locally.
    """
    @staticmethod
    def linear(t: float) -> float:
        return max(0.0, min(1.0, t))

    @staticmethod
    def ease_in(t: float) -> float:
        t = max(0.0, min(1.0, t))
        return t * t * t

    @staticmethod
    def ease_out(t: float) -> float:
        t = max(0.0, min(1.0, t))
        return 1.0 - math.pow(1.0 - t, 3)

    @staticmethod
    def ease_in_out(t: float) -> float:
        t = max(0.0, min(1.0, t))
        return 4.0 * t * t * t if t < 0.5 else 1.0 - math.pow(-2.0 * t + 2.0, 3) / 2.0

    @staticmethod
    def spring(t: float, stiffness: float = 180.0, damping: float = 18.0) -> float:
        t = max(0.0, min(1.0, t))
        decay = math.exp(-damping * t * 4.0)
        oscillation = math.cos(math.sqrt(stiffness) * t * 0.5)
        return 1.0 - decay * oscillation

    @staticmethod
    def elastic(t: float) -> float:
        t = max(0.0, min(1.0, t))
        if t == 0.0:
            return 0.0
        if t == 1.0:
            return 1.0
        return math.pow(2.0, -10.0 * t) * math.sin((t * 10.0 - 0.75) * (2.0 * math.pi / 3.0)) + 1.0

    @staticmethod
    def back(t: float, s: float = 1.70158) -> float:
        t = max(0.0, min(1.0, t))
        return t * t * ((s + 1.0) * t - s)

    @staticmethod
    def bounce(t: float) -> float:
        t = max(0.0, min(1.0, t))
        n1 = 7.5625
        d1 = 2.75
        if t < 1.0 / d1:
            return n1 * t * t
        elif t < 2.0 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375

    @staticmethod
    def overshoot(t: float) -> float:
        t = max(0.0, min(1.0, t))
        return MotionCurves.back(t, s=1.2)

    CURVES: Dict[str, Callable[[float], float]] = {
        "linear": linear.__func__,
        "ease_in": ease_in.__func__,
        "ease_out": ease_out.__func__,
        "ease_in_out": ease_in_out.__func__,
        "spring": spring.__func__,
        "elastic": elastic.__func__,
        "back": back.__func__,
        "bounce": bounce.__func__,
        "overshoot": overshoot.__func__
    }
