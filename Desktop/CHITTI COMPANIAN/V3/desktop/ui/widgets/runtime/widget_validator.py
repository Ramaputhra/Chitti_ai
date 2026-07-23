from typing import Tuple, List, Any

class WidgetValidator:
    """
    S36D-2: Runtime Invariants & Widget Contract Validator for Desktop Widget Framework.
    """
    def validate_widget_invariant(self, widget_action: str) -> Tuple[bool, List[str]]:
        errors = []
        forbidden_actions = [
            "create_window_directly",
            "render_character_png",
            "execute_capability_directly",
            "modify_character_runtime",
            "move_character_window_directly"
        ]
        if widget_action in forbidden_actions:
            errors.append(f"INVARIANT VIOLATION: Widget action '{widget_action}' is strictly prohibited.")
        return len(errors) == 0, errors
