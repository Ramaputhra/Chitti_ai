import time
import threading
from typing import Dict, Any

from desktop.platform.shared.interfaces.event_bus import IEventBus
from desktop.platform.shared.models.event import Event
from desktop.platform.configuration.events import SystemEvents
from desktop.services.logging.logging_service import ILoggingService


class DesktopCaptureProvider:
    """
    Acquires raw screenshots and UI trees from the operating system
    and publishes them to the PerceptionBus.
    For Sprint 33, it publishes mock desktop frames periodically.
    """
    def __init__(self, event_bus: IEventBus, logger: ILoggingService):
        self.event_bus = event_bus
        self.logger = logger
        self._running = False
        self._thread = None
        self.name = "DesktopCaptureProvider"

    def initialize(self):
        pass

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        self.logger.info(f"{self.name} started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        self.logger.info(f"{self.name} stopped")

    def _capture_loop(self):
        while self._running:
            # Simulate a capture every 5 seconds (offset from webcam)
            time.sleep(5)
            if not self._running:
                break
                
            frame_data = {
                "source": "desktop",
                "width": 1920,
                "height": 1080,
                "pixels": b"mock_screenshot_data",
                "active_window_title": "Visual Studio Code",
                "timestamp": time.time()
            }
            
            self.event_bus.publish(
                Event(
                    SystemEvents.FRAME_CAPTURED,
                    self.name,
                    frame_data
                )
            )
            # self.logger.debug("Published FRAME_CAPTURED (desktop)")
