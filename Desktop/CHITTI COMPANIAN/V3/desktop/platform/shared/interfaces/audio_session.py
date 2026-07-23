from desktop.platform.shared.interfaces.service import IService


class IAudioSession(IService):
    """
    Higher-level orchestrator that manages the state of the Microphone and Speaker.
    Handles muting and automatic ducking (lowering volume/pausing mic during playback).
    """
    def mute_microphone(self) -> None:
        """Globally mutes the microphone stream."""
        ...

    def unmute_microphone(self) -> None:
        """Resumes microphone stream."""
        ...

    def set_ducking(self, enabled: bool) -> None:
        """If enabled, microphone is paused when the speaker is active to prevent echo."""
        ...
