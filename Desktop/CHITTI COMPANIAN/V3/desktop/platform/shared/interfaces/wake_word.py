from desktop.platform.shared.interfaces.service import IService


class IWakeWordProvider(IService):
    """
    Interface for Wake Word detection providers.
    E.g. Mock, OpenWakeWord, Porcupine, Neural.
    """
    def start_listening(self) -> None:
        ...

    def stop_listening(self) -> None:
        ...
