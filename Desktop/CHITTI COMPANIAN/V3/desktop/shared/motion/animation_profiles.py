from dataclasses import dataclass
import math
from desktop.shared.motion.motion_tokens import ScaleToken, TimingToken, SPRING_SLIME, SPRING_BREATH

@dataclass
class SlimeDeformation:
    max_stretch: float = 1.05       # Max 5% stretch
    max_compression: float = 0.96   # Max 4% compression
    recovery_spring = SPRING_SLIME

    def calculate_deformation(self, velocity: float) -> float:
        # Clamped deformation within max_compression and max_stretch
        factor = 1.0 + max(-0.04, min(0.05, velocity * 0.01))
        return round(factor, 4)

@dataclass
class BreathingProfile:
    cycle_duration_ms: float = 3000.0  # TimingToken.BREATH (3000ms)
    spring = SPRING_BREATH
    
    def evaluate_amplitude(self, progress: float, base_scale: float = 1.0, max_amplitude: float = 0.03) -> float:
        # Smooth sine breathing cycle
        sine_val = math.sin(progress * 2.0 * math.pi)
        return round(base_scale + sine_val * max_amplitude, 4)

class AnimationProfiles:
    """
    S36E: Canonical Animation Profiles for Slime Motion, Breathing Animation, Waveform,
    Character Motion, Desktop UI, and Presentation.
    """
    SLIME = SlimeDeformation()
    BREATHING_IDLE_DOT = BreathingProfile(cycle_duration_ms=3000.0)
    BREATHING_CHARACTER = BreathingProfile(cycle_duration_ms=3500.0)
    BREATHING_WORKING_DOT = BreathingProfile(cycle_duration_ms=2000.0)
