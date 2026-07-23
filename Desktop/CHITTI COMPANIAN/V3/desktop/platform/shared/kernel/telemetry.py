import json
import threading
import queue
from typing import Any, Dict
from desktop.platform.shared.interfaces.logging import ILoggingService

class TelemetryManager:
    """
    Asynchronous structured telemetry.
    Events are placed on a queue and processed by a background thread
    so that telemetry never blocks execution.
    """
    def __init__(self, logger: ILoggingService) -> None:
        self._logger = logger
        self._queue: queue.Queue = queue.Queue()
        self._running = False
        self._thread: threading.Thread = threading.Thread(target=self._worker_loop, daemon=True)

    def start(self) -> None:
        self._running = True
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        self._queue.put(None)  # Poison pill
        self._thread.join(timeout=2.0)

    def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Non-blocking emit. Puts structured data into the queue.
        """
        payload = {
            "type": event_type,
            "data": data
        }
        self._queue.put(payload)

    def _worker_loop(self) -> None:
        """
        Background thread that drains the queue and formats JSON logs.
        """
        while self._running:
            try:
                item = self._queue.get(timeout=1.0)
                if item is None:
                    break
                
                # Format as structured JSON string for the underlying logger
                json_str = json.dumps(item)
                self._logger.info(f"[TELEMETRY] {json_str}")
                
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self._logger.error(f"TelemetryManager encountered an error: {e}")
