from desktop.platform.shared.interfaces.service import IService


class IMicrophoneManager(IService):
    """
    Manages capturing audio chunks from the OS microphone.
    Emits `Voice.AudioFrame` containing `AudioPacket`s.
    """
    def start_capture(self) -> None:
        """Opens the stream and begins emitting packets."""
        ...

    def stop_capture(self) -> None:
        """Closes the stream."""
        ...
