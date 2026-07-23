import logging
from desktop.ui.window.transparent_window import TransparentWindow
from desktop.ui.animation.motion_runtime_adapter import MotionRuntimeAdapter

logger = logging.getLogger(__name__)

class AnimationEngine:
    """
    S36D-1: Animation Engine executing window opacity, scale, and transform animations.
    """
    def __init__(self):
        self.motion_adapter = MotionRuntimeAdapter()

    def animate_window_scale(self, window: TransparentWindow, start_scale: float, target_scale: float, progress: float):
        factor = self.motion_adapter.evaluate_motion_curve("ease_out", progress)
        window.scale = start_scale + (target_scale - start_scale) * factor
        logger.info(f"[AnimationEngine] Animated window '{window.window_id}' scale to {window.scale:.2f}")
