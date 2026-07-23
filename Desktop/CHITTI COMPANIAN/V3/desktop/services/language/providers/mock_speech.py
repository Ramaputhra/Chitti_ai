import time

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.speech import ISpeechProvider, ISpeechSynthesizer
from desktop.platform.shared.models.audio import AudioPacket


class MockSpeechProvider(ISpeechProvider):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger

    def transcribe(self, packet: AudioPacket) -> str:
        self.logger.info("MockSpeechProvider: Transcribing audio...")
        # Since this is a mock, we will just return a placeholder.
        # Developer injection mode handles bypassing this entirely.
        return "Hello Chitti"


class MockSpeechSynthesizer(ISpeechSynthesizer):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger

    def synthesize(self, text: str) -> AudioPacket:
        self.logger.info(f"MockSpeechSynthesizer: Generating audio for '{text}'")
        # Return a silent 16kHz mono packet simulating a spoken response
        return AudioPacket(
            timestamp=time.time(),
            sample_rate=16000,
            channels=1,
            bit_depth=16,
            frame_count=16000,
            duration=1.0,
            data=bytes(32000),  # 1 sec of silence (2 bytes per frame)
        )
