from typing import List

from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.runtimes.capability.base import BaseCapability
import ctypes

# Virtual Key Codes for Windows Media Controls
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_PLAY_PAUSE = 0xB3

class MediaControlCapability(BaseCapability):
    """
    Controls media playback and system volume using native Windows APIs.
    No automation libraries are required.
    """
    def __init__(self):
        super().__init__()
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "MediaControlCapability"

    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> dict:
        return {"status": "healthy"}

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name="media_control",
            version="1.0",
            category="desktop",
            permissions=["desktop_control"],
            tools=self.discover_tools(),
            health="healthy",
            platform="windows"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(name="media_play_pause", description="Toggle media play/pause.", parameters=[]),
            ToolDescriptor(name="media_next_track", description="Skip to next track.", parameters=[]),
            ToolDescriptor(name="media_prev_track", description="Go to previous track.", parameters=[]),
            ToolDescriptor(name="volume_up", description="Increase system volume.", parameters=[]),
            ToolDescriptor(name="volume_down", description="Decrease system volume.", parameters=[]),
            ToolDescriptor(name="volume_mute", description="Toggle system mute.", parameters=[]),
        ]

    def _press_key(self, key_code: int) -> None:
        # Key down
        ctypes.windll.user32.keybd_event(key_code, 0, 0, 0)
        # Key up
        ctypes.windll.user32.keybd_event(key_code, 0, 2, 0)

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        try:
            if invocation.tool_name == "media_play_pause":
                self._press_key(VK_MEDIA_PLAY_PAUSE)
            elif invocation.tool_name == "media_next_track":
                self._press_key(VK_MEDIA_NEXT_TRACK)
            elif invocation.tool_name == "media_prev_track":
                self._press_key(VK_MEDIA_PREV_TRACK)
            elif invocation.tool_name == "volume_up":
                self._press_key(VK_VOLUME_UP)
            elif invocation.tool_name == "volume_down":
                self._press_key(VK_VOLUME_DOWN)
            elif invocation.tool_name == "volume_mute":
                self._press_key(VK_VOLUME_MUTE)
            else:
                return ExecutionResult(success=False, error=f"Unknown tool: {invocation.tool_name}")
                
            return ExecutionResult(success=True, output=f"Executed {invocation.tool_name} successfully.")
        except Exception as e:
            return ExecutionResult(success=False, error=str(e))
