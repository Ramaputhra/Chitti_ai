from typing import Protocol

from desktop.platform.shared.models.audio import AudioPacket


class IAudioFormatManager(Protocol):
    """
    Handles conversion of audio between different sample rates, depths, and channels.
    Ensures STT engines always receive the exact format they expect.
    """
    def to_standard_format(self, packet: AudioPacket) -> AudioPacket:
        """
        Converts any incoming packet into the CHITTI standard:
        16kHz, 16-bit PCM, Mono, Little Endian.
        """
        ...
