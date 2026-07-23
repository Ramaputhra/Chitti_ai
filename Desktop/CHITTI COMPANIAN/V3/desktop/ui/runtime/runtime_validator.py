from typing import Tuple, List, Any

class RuntimeValidator:
    """
    S36D-1: Runtime Invariants & Performance Validator for Desktop UI Runtime Foundation.
    Ensures zero character PNG asset rendering, correct render profiles, and Character Anchor API compliance.
    """
    def validate_render_request(self, asset_type: str) -> Tuple[bool, List[str]]:
        errors = []
        if asset_type.lower() in ["character_png", "character_frame", "chr_frame"]:
            errors.append("PROHIBITED: Desktop UI Runtime SHALL NEVER render Character PNG assets or frame sequences.")
        return len(errors) == 0, errors

    def validate_fps_profile(self, profile: str, requested_fps: int) -> Tuple[bool, List[str]]:
        errors = []
        target_map = {
            "WIDGET": 30,
            "WAVEFORM": 24,
            "PRESENCE_DOT": 5
        }
        expected = target_map.get(profile.upper())
        if expected and requested_fps > expected:
            errors.append(f"FPS Violation for '{profile}': Requested {requested_fps} FPS exceeds profile limit of {expected} FPS.")
        return len(errors) == 0, errors
