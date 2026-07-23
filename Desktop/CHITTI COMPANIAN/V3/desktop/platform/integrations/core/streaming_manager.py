from typing import Any, Dict, Generator

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.streaming_manager import IStreamingManager


class StreamingManager(IStreamingManager):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED
        self._active_streams: Dict[str, bool] = {}

    @property
    def name(self) -> str:
        return "StreamingManager"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        for sid in list(self._active_streams.keys()):
            self.cancel_stream(sid)
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {"active_streams_count": len(self._active_streams)}

    def process_stream(
        self, stream_id: str, data_stream: Generator[Any, None, None]
    ) -> Generator[Any, None, None]:
        self._active_streams[stream_id] = True
        self.logger.info(f"Stream {stream_id} started")
        try:
            for item in data_stream:
                if not self._active_streams.get(stream_id, False):
                    self.logger.info(f"Stream {stream_id} cancelled during processing")
                    break
                yield item
        finally:
            if stream_id in self._active_streams:
                del self._active_streams[stream_id]
            self.logger.info(f"Stream {stream_id} completed or cleaned up")

    def process_cognitive_stream(
        self, stream_id: str, data_stream: Generator[Any, None, None]
    ) -> Generator[Any, None, None]:
        self._active_streams[stream_id] = True
        self.logger.info(f"Cognitive stream {stream_id} started")
        buffer = ""
        try:
            for item in data_stream:
                if not self._active_streams.get(stream_id, False):
                    break
                
                # Conceptually: Buffer -> Sentence -> Parse -> Dispatch
                # Yield parsed sentences or partial objects
                text_chunk = getattr(item, "text", str(item))
                buffer += text_chunk
                
                # Mock sentence builder boundary
                if "." in text_chunk or "\n" in text_chunk:
                    yield buffer.strip()
                    buffer = ""
                    
            if buffer:
                yield buffer.strip()
        finally:
            if stream_id in self._active_streams:
                del self._active_streams[stream_id]
            self.logger.info(f"Cognitive stream {stream_id} completed")

    def cancel_stream(self, stream_id: str) -> None:
        if stream_id in self._active_streams:
            self._active_streams[stream_id] = False
            self.logger.info(f"Stream {stream_id} marked for cancellation")
