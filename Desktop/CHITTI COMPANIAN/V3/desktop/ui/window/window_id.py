from enum import Enum

class CanonicalWindowID(Enum):
    UI_WINDOW_CHARACTER_WIDGET = "UI_WINDOW_CHARACTER_WIDGET"
    UI_WINDOW_NOTIFICATION = "UI_WINDOW_NOTIFICATION"
    UI_WINDOW_DIALOG = "UI_WINDOW_DIALOG"
    UI_WINDOW_FLOATING = "UI_WINDOW_FLOATING"
    UI_WINDOW_OVERLAY = "UI_WINDOW_OVERLAY"
    UI_WINDOW_EDGE = "UI_WINDOW_EDGE"
    UI_WINDOW_POPUP = "UI_WINDOW_POPUP"
    UI_WINDOW_SYSTEM = "UI_WINDOW_SYSTEM"
    UI_WINDOW_DEBUG = "UI_WINDOW_DEBUG"

class WindowIDGenerator:
    """
    S36D-1-R1: Generates permanent canonical window identifiers without relying on runtime memory addresses.
    """
    @staticmethod
    def get_canonical_id(window_type: str, instance_key: str = "default") -> str:
        prefix_map = {
            "CharacterWidget": "UI_WINDOW_CHARACTER_WIDGET",
            "NotificationWindow": "UI_WINDOW_NOTIFICATION",
            "DialogWindow": "UI_WINDOW_DIALOG",
            "FloatingWindow": "UI_WINDOW_FLOATING",
            "OverlayWindow": "UI_WINDOW_OVERLAY",
            "EdgeWindow": "UI_WINDOW_EDGE",
            "PopupWindow": "UI_WINDOW_POPUP",
            "SystemWindow": "UI_WINDOW_SYSTEM",
            "DebugWindow": "UI_WINDOW_DEBUG"
        }
        prefix = prefix_map.get(window_type, "UI_WINDOW_FLOATING")
        return f"{prefix}_{instance_key.upper()}"
