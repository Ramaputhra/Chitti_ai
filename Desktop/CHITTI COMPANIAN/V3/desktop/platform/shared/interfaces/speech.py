from typing import Protocol

from typing import Generator

from desktop.platform.shared.models.audio import AudioPacket, TranscriptionResult
from desktop.platform.shared.interfaces.provider import IProvider

class ISpeechProvider(IProvider):
    """
    Translates AudioPackets into raw text transcriptions (Speech-to-Text).
    """
    def transcribe(self, packet: AudioPacket) -> TranscriptionResult:
        ...


class ISpeechSynthesizer(IProvider):
    """
    Converts text back into spoken audio bytes.
    """
    def synthesize(self, text: str, language: str = "en") -> bytes:
        ...

    def synthesize_stream(self, text: str, language: str = "en") -> Generator[bytes, None, None]:
        ...
