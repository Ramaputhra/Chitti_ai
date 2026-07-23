from desktop.platform.shared.interfaces.service import IService


class IVoiceFocusManager(IService):
    """
    Manages priority access to the physical audio pipeline to prevent feedback loops.
    """
    def request_focus(self, requester: str, priority: int) -> bool:
        ...

    def release_focus(self, requester: str) -> None:
        ...
