import queue
import threading
from typing import Any, Dict

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import IService, ServiceState
from desktop.platform.inference.local.piper.piper_provider import PiperProvider


class NotificationQueue(IService):
    """
    Lightweight queue to prevent TTS from interrupting itself.
    Processes synthesized speech sequentially.
    """
    def __init__(self, logger: ILoggingService, tts: PiperProvider) -> None:
        self.logger = logger
        self.tts = tts
        self._state = ServiceState.STOPPED
        self._queue = queue.Queue(maxsize=50) # Bounded to prevent memory explosion
        self._worker_thread = None
        self._is_paused = False

    @property
    def name(self) -> str:
        return "NotificationQueue"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self.logger.info(f"{self.name} initialized")

    def start(self) -> None:
        if self._state == ServiceState.RUNNING: return
        self._state = ServiceState.RUNNING
        self._is_paused = False
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True, name="Thread-NotificationQueue")
        self._worker_thread.start()
        self.logger.info(f"{self.name} started")

    def pause(self) -> None:
        self._is_paused = True
        self.logger.info(f"{self.name} paused")

    def resume(self) -> None:
        self._is_paused = False
        self.logger.info(f"{self.name} resumed")

    def recover(self) -> None:
        self.logger.info(f"{self.name} recovering. Clearing queue.")
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break
        self._state = ServiceState.STOPPED
        self.start()

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        # Put a sentinel to break the loop
        try:
            self._queue.put(None, timeout=1.0)
        except queue.Full:
            pass
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2.0)
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {
            "queue_size": self._queue.qsize(),
            "max_size": 50,
            "paused": self._is_paused,
            "thread_alive": self._worker_thread.is_alive() if self._worker_thread else False
        }

    def enqueue(self, text: str) -> None:
        """Adds text to be spoken sequentially."""
        if not text or not text.strip():
            return
        if self._state != ServiceState.RUNNING:
            return
        try:
            self._queue.put(text, block=False)
            self.logger.info(f"Notification enqueued: '{text[:30]}...'")
        except queue.Full:
            self.logger.warning(f"NotificationQueue overflow! Dropping notification: '{text[:30]}...'")

    def _process_queue(self) -> None:
        while self._state == ServiceState.RUNNING:
            try:
                item = self._queue.get(timeout=0.5)
                if item is None:
                    break
                    
                if self._is_paused:
                    # If paused, we put it back and wait
                    self._queue.put(item)
                    time.sleep(1.0)
                    continue

                self.logger.info(f"Processing notification from queue...")
                # The tts.speak method will block until the audio finishes playing
                self.tts.speak(item)
                
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing notification queue: {e}")
