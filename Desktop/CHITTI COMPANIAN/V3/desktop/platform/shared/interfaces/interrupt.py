from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.interrupt import InterruptReason


class IInterruptManager(IService):
    """
    Handles system and user interrupts safely canceling active processing/playback.
    """
    def trigger_interrupt(self, reason: InterruptReason, details: str = "") -> None:
        ...
