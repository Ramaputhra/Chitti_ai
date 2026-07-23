import logging
import threading
import queue
from typing import Optional, Any

logger = logging.getLogger(__name__)

class AudioCaptureService:
    """
    Captures raw audio from the default microphone and buffers it.
    Uses a background thread to prevent blocking the main event loop.
    Mocked implementation until pyaudio/sounddevice dependencies are formally added.
    """
    def __init__(self, event_bus: Any, sample_rate: int = 16000, chunk_size: int = 512):
        self.event_bus = event_bus
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self._audio_queue: queue.Queue = queue.Queue()
        self._is_recording = False
        self._capture_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._is_recording:
            return
            
        self._is_recording = True
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()
        logger.info("AudioCaptureService started. Listening to microphone...")

    def stop(self) -> None:
        self._is_recording = False
        if self._capture_thread:
            self._capture_thread.join(timeout=1.0)
        logger.info("AudioCaptureService stopped.")

    def _capture_loop(self) -> None:
        """
        In a real implementation, this reads from pyaudio.Stream.
        For now, it just yields synthetic silence or test buffers.
        """
        import time
        while self._is_recording:
            # Mocking audio chunk capture
            time.sleep(self.chunk_size / self.sample_rate)
            # Create a mock silent audio chunk (bytes)
            chunk = b'\x00' * (self.chunk_size * 2) # 16-bit PCM
            self.event_bus.publish("AUDIO_CHUNK_CAPTURED", source="AudioCaptureService", payload={"data": chunk})
            
    def get_queue(self) -> queue.Queue:
        return self._audio_queue
