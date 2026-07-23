import time
import asyncio
import logging
from typing import List, Optional, Any, Dict
from desktop.models.lifecycle import IRuntime, HealthState
from desktop.models.analytics import UserActivityEvent

logger = logging.getLogger(__name__)

def get_active_window_info() -> Dict[str, str]:
    """
    OS API helper to retrieve foreground window and application title.
    Falls back gracefully across platforms or headless test environments.
    """
    try:
        import ctypes
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if hwnd:
            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value or "Desktop"
            
            # Simple app name extraction from title or generic
            app_name = "Desktop"
            if " - " in title:
                app_name = title.split(" - ")[-1].strip()
            elif " " in title:
                app_name = title.split()[0].strip()
            return {"app_name": app_name, "window_title": title}
    except Exception:
        pass
    return {"app_name": "Desktop", "window_title": "Active Desktop Window"}

class DesktopActivityRuntime(IRuntime):
    """
    S32B: Desktop Activity Platform service.
    Monitors active application and window transitions, publishing UserActivityEvent objects onto EventBus.
    Communicates EXCLUSIVELY via EventBus. Zero direct storage access.
    """
    def __init__(self, poll_interval_sec: float = 1.0):
        self._running = False
        self._context = None
        self.poll_interval_sec = poll_interval_sec
        self.current_app = ""
        self.current_window = ""
        self.last_switch_time = time.time()

    @property
    def dependencies(self):
        return []

    def health(self) -> HealthState:
        return HealthState.HEALTHY if self._running else HealthState.DEGRADED

    async def initialize(self, context: Any = None) -> bool:
        self._context = context
        logger.info("[DesktopActivityRuntime] Initialized desktop activity platform service.")
        return True

    async def start(self) -> bool:
        self._running = True
        logger.info("[DesktopActivityRuntime] Started desktop activity monitoring.")
        return True

    async def stop(self) -> bool:
        self._running = False
        logger.info("[DesktopActivityRuntime] Stopped desktop activity monitoring.")
        return True

    async def shutdown(self) -> bool:
        await self.stop()
        return True

    def record_activity(self, app_name: str, window_title: str, duration_ms: float = 0.0, session_id: str = "global") -> Optional[UserActivityEvent]:
        """
        Records a window activity change and publishes UserActivityEvent to EventBus.
        """
        now = time.time()
        event = UserActivityEvent(
            app_name=app_name,
            window_title=window_title,
            duration_ms=duration_ms,
            session_id=session_id,
            timestamp=now
        )

        self.current_app = app_name
        self.current_window = window_title
        self.last_switch_time = now

        if self._context and hasattr(self._context, "event_bus"):
            self._context.event_bus.publish(event)
            logger.debug(f"[DesktopActivityRuntime] Published UserActivityEvent for '{app_name}'.")

        return event

    def poll_active_window(self, session_id: str = "global") -> Optional[UserActivityEvent]:
        """
        Polls OS active window and emits UserActivityEvent if window focus changed.
        """
        info = get_active_window_info()
        app_name = info["app_name"]
        window_title = info["window_title"]
        now = time.time()

        if app_name != self.current_app or window_title != self.current_window:
            duration_ms = max(0.0, (now - self.last_switch_time) * 1000.0)
            return self.record_activity(app_name, window_title, duration_ms=duration_ms, session_id=session_id)
        
        return None
