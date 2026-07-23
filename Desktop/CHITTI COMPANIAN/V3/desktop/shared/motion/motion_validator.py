from typing import Tuple, List, Any
from desktop.shared.motion.motion_tokens import SpringToken, ScaleToken

class MotionValidator:
    """
    S36E: Motion Validator ensuring no hardcoded local animation durations, spring values,
    or out-of-bounds slime deformations exist across runtimes.
    """
    def validate_spring(self, spring: SpringToken) -> Tuple[bool, List[str]]:
        errors = []
        if spring.stiffness < 10.0 or spring.stiffness > 500.0:
            errors.append(f"Stiffness '{spring.stiffness}' outside valid range (10-500).")
        if spring.damping < 1.0 or spring.damping > 100.0:
            errors.append(f"Damping '{spring.damping}' outside valid range (1-100).")
        return len(errors) == 0, errors

    def validate_slime_deformation(self, scale: float) -> Tuple[bool, List[str]]:
        errors = []
        if scale > ScaleToken.SLIME_STRETCH.value:
            errors.append(f"Slime stretch '{scale}' exceeds 5% limit ({ScaleToken.SLIME_STRETCH.value}).")
        if scale < ScaleToken.SLIME_COMPRESS.value:
            errors.append(f"Slime compression '{scale}' exceeds 4% limit ({ScaleToken.SLIME_COMPRESS.value}).")
        return len(errors) == 0, errors
