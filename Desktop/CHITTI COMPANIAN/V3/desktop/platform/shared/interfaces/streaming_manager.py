from typing import Any, Generator

from desktop.platform.shared.interfaces.service import IService


class IStreamingManager(IService):
    """
    Infrastructural streaming engine that handles backpressure, chunking,
    and cancellation for any stream (Speech, TTS, LLM).
    """
    def process_stream(
        self, stream_id: str, data_stream: Generator[Any, None, None]
    ) -> Generator[Any, None, None]:
        ...
        
    def process_cognitive_stream(
        self, stream_id: str, data_stream: Generator[Any, None, None]
    ) -> Generator[Any, None, None]:
        """
        Passes a cognitive stream through Token Buffer -> Sentence Builder -> 
        Incremental Parser -> Event Dispatcher yielding partial parsed items.
        """
        ...

    def cancel_stream(self, stream_id: str) -> None:
        ...
