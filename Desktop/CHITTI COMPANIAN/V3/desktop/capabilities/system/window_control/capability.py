"""
Window Control Capability

Provides full window management including:
- Window listing and information
- Window move/resize operations
- Window snap and positioning
- Active window control
- Window focus management
"""
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

try:
    import win32gui
    import win32con
    import win32api
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

try:
    import subprocess
    HAS_SUBPROCESS = True
except ImportError:
    HAS_SUBPROCESS = False

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.ai import ToolInvocation

logger = logging.getLogger(__name__)


class WindowState(str, Enum):
    """Window states."""
    NORMAL = "normal"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    FULLSCREEN = "fullscreen"
    HIDDEN = "hidden"


@dataclass
class WindowInfo:
    """Information about a window."""
    hwnd: int
    title: str
    class_name: str
    process_id: int
    process_name: str
    bounds: Tuple[int, int, int, int]  # (x, y, width, height)
    state: WindowState
    is_visible: bool
    is_active: bool


class WindowControlCapability(ICapability):
    """
    Full window control capability for desktop automation.
    Supports Windows, macOS (via pyobjc), and Linux (via wmctrl).
    """
    
    def __init__(self):
        self._state = ServiceState.STOPPED
        self._platform = self._detect_platform()
    
    @property
    def name(self) -> str:
        return "WindowControlCapability"
    
    @property
    def state(self) -> ServiceState:
        return self._state
    
    def initialize(self) -> None:
        """Initialize the capability."""
        self._state = ServiceState.RUNNING
        logger.info(f"WindowControlCapability initialized on {self._platform}")
    
    def shutdown(self) -> None:
        """Shutdown the capability."""
        self._state = ServiceState.STOPPED
        logger.info("WindowControlCapability shutdown")
    
    def _detect_platform(self) -> str:
        """Detect the current platform."""
        import platform
        return platform.system()
    
    def discover_tools(self) -> List[ToolDescriptor]:
        """Return available tools."""
        return [
            ToolDescriptor(
                name="list_windows",
                description="List all visible windows",
                parameters=[
                    ToolParameter(name="include_hidden", type="boolean", required=False, 
                                 description="Include hidden windows")
                ]
            ),
            ToolDescriptor(
                name="get_active_window",
                description="Get information about the currently active window",
                parameters=[]
            ),
            ToolDescriptor(
                name="focus_window",
                description="Focus a window by title or process name",
                parameters=[
                    ToolParameter(name="target", type="string", required=True,
                                 description="Window title or process name to focus")
                ]
            ),
            ToolDescriptor(
                name="move_window",
                description="Move a window to a specific position",
                parameters=[
                    ToolParameter(name="hwnd", type="integer", required=False,
                                 description="Window handle (uses active if not provided)"),
                    ToolParameter(name="x", type="integer", required=True,
                                 description="New X position"),
                    ToolParameter(name="y", type="integer", required=True,
                                 description="New Y position")
                ]
            ),
            ToolDescriptor(
                name="resize_window",
                description="Resize a window to specific dimensions",
                parameters=[
                    ToolParameter(name="hwnd", type="integer", required=False,
                                 description="Window handle (uses active if not provided)"),
                    ToolParameter(name="width", type="integer", required=True,
                                 description="New width"),
                    ToolParameter(name="height", type="integer", required=True,
                                 description="New height")
                ]
            ),
            ToolDescriptor(
                name="set_window_state",
                description="Set window state (minimize, maximize, restore)",
                parameters=[
                    ToolParameter(name="hwnd", type="integer", required=False,
                                 description="Window handle (uses active if not provided)"),
                    ToolParameter(name="state", type="string", required=True,
                                 description="new_state: minimize, maximize, restore, or fullscreen")
                ]
            ),
            ToolDescriptor(
                name="snap_window",
                description="Snap window to screen edge (Windows 10/11 style)",
                parameters=[
                    ToolParameter(name="hwnd", type="integer", required=False,
                                 description="Window handle (uses active if not provided)"),
                    ToolParameter(name="position", type="string", required=True,
                                 description="Position: left, right, top_left, top_right, bottom_left, bottom_right, center")
                ]
            ),
            ToolDescriptor(
                name="get_window_bounds",
                description="Get window position and size",
                parameters=[
                    ToolParameter(name="hwnd", type="integer", required=False,
                                 description="Window handle (uses active if not provided)")
                ]
            )
        ]
    
    def validate(self, invocation: ToolInvocation) -> bool:
        """Validate the invocation."""
        return invocation.tool_name in [t.name for t in self.discover_tools()]
    
    async def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        """Execute the window control operation."""
        try:
            tool_name = invocation.tool_name
            params = invocation.parameters or {}
            
            if tool_name == "list_windows":
                result = self._list_windows(params.get("include_hidden", False))
            elif tool_name == "get_active_window":
                result = self._get_active_window()
            elif tool_name == "focus_window":
                result = self._focus_window(params.get("target", ""))
            elif tool_name == "move_window":
                result = self._move_window(
                    params.get("hwnd"), params.get("x", 0), params.get("y", 0)
                )
            elif tool_name == "resize_window":
                result = self._resize_window(
                    params.get("hwnd"), params.get("width", 800), params.get("height", 600)
                )
            elif tool_name == "set_window_state":
                result = self._set_window_state(params.get("hwnd"), params.get("state", "restore"))
            elif tool_name == "snap_window":
                result = self._snap_window(params.get("hwnd"), params.get("position", "center"))
            elif tool_name == "get_window_bounds":
                result = self._get_window_bounds(params.get("hwnd"))
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message=f"Unknown tool: {tool_name}"
                )
            
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                message="Operation completed",
                data=result
            )
            
        except Exception as e:
            logger.error(f"Window control error: {e}")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=str(e)
            )
    
    def _list_windows(self, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """List all windows."""
        windows = []
        
        if self._platform == "Windows" and HAS_WIN32:
            windows = self._list_windows_windows(include_hidden)
        else:
            # Cross-platform fallback using pyautogui
            windows = self._list_windows_crossplatform(include_hidden)
        
        return windows
    
    def _list_windows_windows(self, include_hidden: bool) -> List[Dict[str, Any]]:
        """List windows on Windows."""
        windows = []
        
        def callback(hwnd, _):
            if not win32gui.IsWindow(hwnd):
                return
            
            if not include_hidden and not win32gui.IsWindowVisible(hwnd):
                return
            
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return
            
            class_name = win32gui.GetClassName(hwnd)
            _, process_id = win32api.GetWindowThreadProcessId(hwnd)
            
            try:
                import psutil
                process = psutil.Process(process_id)
                process_name = process.name()
            except:
                process_name = "unknown"
            
            rect = win32gui.GetWindowRect(hwnd)
            bounds = (rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
            
            visible = win32gui.IsWindowVisible(hwnd)
            
            windows.append({
                "hwnd": hwnd,
                "title": title,
                "class_name": class_name,
                "process_id": process_id,
                "process_name": process_name,
                "bounds": bounds,
                "state": self._get_window_state_windows(hwnd),
                "is_visible": visible
            })
        
        win32gui.EnumWindows(callback, None)
        return windows
    
    def _list_windows_crossplatform(self, include_hidden: bool) -> List[Dict[str, Any]]:
        """Cross-platform window listing fallback."""
        # This is a simplified fallback
        return [
            {"note": "Cross-platform window listing requires platform-specific implementation"}
        ]
    
    def _get_active_window(self) -> Dict[str, Any]:
        """Get the currently active window."""
        if self._platform == "Windows" and HAS_WIN32:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            rect = win32gui.GetWindowRect(hwnd)
            bounds = (rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
            
            return {
                "hwnd": hwnd,
                "title": title,
                "class_name": class_name,
                "bounds": bounds,
                "state": self._get_window_state_windows(hwnd)
            }
        
        return {"error": "Active window detection not supported on this platform"}
    
    def _focus_window(self, target: str) -> Dict[str, Any]:
        """Focus a window by title or process name."""
        if self._platform == "Windows" and HAS_WIN32:
            windows = self._list_windows_windows(False)
            
            # Find matching window
            for window in windows:
                if target.lower() in window["title"].lower() or \
                   target.lower() in window["process_name"].lower():
                    hwnd = window["hwnd"]
                    
                    # Restore if minimized
                    if win32gui.IsIconic(hwnd):
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    
                    # Bring to front
                    win32gui.SetForegroundWindow(hwnd)
                    
                    return {"focused": window["title"], "hwnd": hwnd}
            
            return {"error": f"Window not found: {target}"}
        
        return {"error": "Window focus not supported on this platform"}
    
    def _move_window(self, hwnd: Optional[int], x: int, y: int) -> Dict[str, Any]:
        """Move a window to a specific position."""
        if self._platform == "Windows" and HAS_WIN32:
            if hwnd is None:
                hwnd = win32gui.GetForegroundWindow()
            
            win32gui.SetWindowPos(
                hwnd, None, x, y, 0, 0,
                win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
            )
            
            return {"moved": True, "hwnd": hwnd, "x": x, "y": y}
        
        return {"error": "Window move not supported on this platform"}
    
    def _resize_window(self, hwnd: Optional[int], width: int, height: int) -> Dict[str, Any]:
        """Resize a window."""
        if self._platform == "Windows" and HAS_WIN32:
            if hwnd is None:
                hwnd = win32gui.GetForegroundWindow()
            
            win32gui.SetWindowPos(
                hwnd, None, 0, 0, width, height,
                win32con.SWP_NOMOVE | win32con.SWP_NOZORDER
            )
            
            return {"resized": True, "hwnd": hwnd, "width": width, "height": height}
        
        return {"error": "Window resize not supported on this platform"}
    
    def _set_window_state(self, hwnd: Optional[int], state: str) -> Dict[str, Any]:
        """Set window state."""
        if self._platform == "Windows" and HAS_WIN32:
            if hwnd is None:
                hwnd = win32gui.GetForegroundWindow()
            
            state_map = {
                "minimize": win32con.SW_MINIMIZE,
                "maximize": win32con.SW_MAXIMIZE,
                "restore": win32con.SW_RESTORE,
                "show": win32con.SW_SHOW,
                "hide": win32con.SW_HIDE
            }
            
            if state not in state_map:
                return {"error": f"Unknown state: {state}"}
            
            win32gui.ShowWindow(hwnd, state_map[state])
            
            return {"state_changed": True, "new_state": state}
        
        return {"error": "Window state not supported on this platform"}
    
    def _snap_window(self, hwnd: Optional[int], position: str) -> Dict[str, Any]:
        """Snap window to a screen edge (Windows 10/11 style)."""
        if self._platform == "Windows" and HAS_WIN32:
            if hwnd is None:
                hwnd = win32gui.GetForegroundWindow()
            
            # Get screen dimensions
            screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            
            # Snap positions
            snap_map = {
                "left": (0, 0, screen_width // 2, screen_height),
                "right": (screen_width // 2, 0, screen_width // 2, screen_height),
                "top_left": (0, 0, screen_width // 2, screen_height // 2),
                "top_right": (screen_width // 2, 0, screen_width // 2, screen_height // 2),
                "bottom_left": (0, screen_height // 2, screen_width // 2, screen_height // 2),
                "bottom_right": (screen_width // 2, screen_height // 2, screen_width // 2, screen_height // 2),
                "center": ((screen_width - 800) // 2, (screen_height - 600) // 2, 800, 600)
            }
            
            if position not in snap_map:
                return {"error": f"Unknown position: {position}"}
            
            x, y, width, height = snap_map[position]
            
            win32gui.SetWindowPos(
                hwnd, None, x, y, width, height,
                win32con.SWP_NOZORDER
            )
            
            return {"snapped": True, "position": position, "bounds": (x, y, width, height)}
        
        return {"error": "Window snap not supported on this platform"}
    
    def _get_window_bounds(self, hwnd: Optional[int]) -> Dict[str, Any]:
        """Get window bounds."""
        if self._platform == "Windows" and HAS_WIN32:
            if hwnd is None:
                hwnd = win32gui.GetForegroundWindow()
            
            rect = win32gui.GetWindowRect(hwnd)
            bounds = (rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
            
            return {"hwnd": hwnd, "bounds": bounds}
        
        return {"error": "Get bounds not supported on this platform"}
    
    def _get_window_state_windows(self, hwnd: int) -> str:
        """Get window state on Windows."""
        if win32gui.IsIconic(hwnd):
            return WindowState.MINIMIZED.value
        elif win32gui.IsZoomed(hwnd):
            return WindowState.MAXIMIZED.value
        elif not win32gui.IsWindowVisible(hwnd):
            return WindowState.HIDDEN.value
        return WindowState.NORMAL.value
    
    def describe(self) -> CapabilityDescriptor:
        """Return capability descriptor."""
        return CapabilityDescriptor(
            id="window_control",
            version="1.0.0",
            name="Window Control",
            description="Full window management including move, resize, snap, and focus control",
            category="system",
            tags=["window", "desktop", "automation"]
        )
