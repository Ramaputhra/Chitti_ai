from typing import Any, Callable, Dict

from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.attention import AttentionEvent


class IPerceptionBus(IService):
    """
    The universal ingestion layer for all multimodal inputs.
    It takes raw payloads from Vision, Audio, OS, Robot, Calendar, etc.,
    and normalizes them into AttentionEvents.
    """
    def publish_raw(self, source: str, category: str, target: str, payload: Dict[str, Any]) -> None:
        ...

    def subscribe(self, callback: Callable[[AttentionEvent], None]) -> None:
        ...
