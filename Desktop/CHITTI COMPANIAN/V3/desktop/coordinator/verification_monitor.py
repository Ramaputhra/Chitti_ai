from typing import Tuple, List

class VerificationMonitor:
    """S36E: Verification Monitor enforcing Visual Coordinator Runtime Invariants."""
    def validate_action(self, action: str) -> Tuple[bool, List[str]]:
        forbidden = [
            "render_ui_directly",
            "render_character_directly",
            "create_windows_directly",
            "create_widgets_directly",
            "execute_capability_directly",
            "access_runtime_internals"
        ]
        errors = []
        if action in forbidden:
            errors.append(f"COORDINATOR INVARIANT VIOLATION: Action '{action}' is strictly prohibited.")
        return len(errors) == 0, errors
