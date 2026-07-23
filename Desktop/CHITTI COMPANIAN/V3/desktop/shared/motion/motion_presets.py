from desktop.shared.motion.motion_registry import MOTION_REGISTRY
from desktop.shared.motion.motion_tokens import TimingToken, OpacityToken, ScaleToken

class MotionPresets:
    """
    S36E: Higher-level Preset combinations for UI & Character Animations.
    """
    WAKE_PRESET = {
        "spring": MOTION_REGISTRY.get_spring("Wake"),
        "timing": TimingToken.MEDIUM.value,
        "opacity": OpacityToken.ACTIVE.value,
        "scale": ScaleToken.EXPANDED.value
    }

    DOCK_PRESET = {
        "spring": MOTION_REGISTRY.get_spring("Dock"),
        "timing": TimingToken.NORMAL.value,
        "opacity": OpacityToken.NOTIFICATION.value,
        "scale": ScaleToken.DOCKED.value
    }

    SLIME_PRESET = {
        "spring": MOTION_REGISTRY.get_spring("Slime"),
        "timing": TimingToken.FAST.value,
        "max_stretch": ScaleToken.SLIME_STRETCH.value,
        "max_compress": ScaleToken.SLIME_COMPRESS.value
    }
