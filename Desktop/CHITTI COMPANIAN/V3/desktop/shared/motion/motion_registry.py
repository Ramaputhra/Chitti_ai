import logging
from typing import Dict, Any, Optional, Callable
from desktop.shared.motion.motion_tokens import SpringToken, TimingToken, OpacityToken, ScaleToken
from desktop.shared.motion.spring_profiles import SpringProfiles
from desktop.shared.motion.motion_curves import MotionCurves
from desktop.shared.motion.animation_profiles import AnimationProfiles

logger = logging.getLogger(__name__)

class MotionRegistry:
    """
    S36E: Centralized Motion Registry.
    The ONLY source of motion definitions across the entire CHITTI platform.
    Supports hot-reloading motion profiles during development.
    """
    def __init__(self):
        self._springs: Dict[str, SpringToken] = dict(SpringProfiles.PROFILES)
        self._curves: Dict[str, Callable[[float], float]] = dict(MotionCurves.CURVES)
        self.animation_profiles = AnimationProfiles()
        self.reload_count = 0
        logger.info("[MotionRegistry] Motion Design System Registry initialized cleanly.")

    def get_spring(self, name: str) -> Optional[SpringToken]:
        return self._springs.get(name)

    def get_curve(self, name: str) -> Optional[Callable[[float], float]]:
        return self._curves.get(name)

    def register_spring(self, name: str, spring: SpringToken):
        self._springs[name] = spring
        logger.info(f"[MotionRegistry] Registered custom spring: '{name}'")

    def hot_reload(self) -> bool:
        """
        Hot reloads motion profiles during development without restarting the application.
        """
        self._springs = dict(SpringProfiles.PROFILES)
        self._curves = dict(MotionCurves.CURVES)
        self.reload_count += 1
        logger.info(f"[MotionRegistry] Motion profiles hot-reloaded successfully (Count: {self.reload_count}).")
        return True

# Canonical singleton instance
MOTION_REGISTRY = MotionRegistry()
