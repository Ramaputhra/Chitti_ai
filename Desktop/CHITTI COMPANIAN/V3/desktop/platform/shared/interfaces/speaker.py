from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.audio import AudioPacket


class ISpeakerManager(IService):
    """
    Manages audio playback through the OS speakers.
    """
    def play(self, packet: AudioPacket) -> None:
        """Plays an audio packet."""
        ...

    def stop_playback(self) -> None:
        """Immediately stops all active playback."""
        ...
