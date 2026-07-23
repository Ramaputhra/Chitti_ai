from typing import Dict, Any, Tuple

class SemanticObservationProvider:
    """
    Platform-independent interface for extracting deterministic UI information.
    Prioritized over Vision AI per Rule 128.
    """
    def capture_screenshot(self) -> str:
        """Returns the file path or base64 of the screen capture."""
        raise NotImplementedError
        
    def get_ui_tree(self) -> Dict[str, Any]:
        """Returns the accessibility tree (UIA, AT-SPI, Mac Accessibility)."""
        raise NotImplementedError
        
    def get_window_metadata(self) -> Dict[str, Any]:
        """Returns z-order, window titles, process names."""
        raise NotImplementedError
        
    def get_clipboard_text(self) -> str:
        raise NotImplementedError

class WindowsSemanticProvider(SemanticObservationProvider):
    """
    Windows implementation using UIAutomation and Win32 APIs.
    """
    def capture_screenshot(self) -> str:
        # Stub: PyAutoGUI or MSS implementation
        return "/tmp/screenshot.png"
        
    def get_ui_tree(self) -> Dict[str, Any]:
        # Stub: Use pyuiautomation or similar to dump the semantic tree
        return {
            "type": "Window",
            "name": "Visual Studio Code",
            "children": [
                {"type": "Document", "name": "main.py"},
                {"type": "Button", "name": "Run"}
            ]
        }
        
    def get_window_metadata(self) -> Dict[str, Any]:
        # Stub: Use EnumWindows to get active context
        return {
            "active_window": "main.py - Visual Studio Code",
            "process": "Code.exe"
        }
        
    def get_clipboard_text(self) -> str:
        return "def calculate_sum():"
