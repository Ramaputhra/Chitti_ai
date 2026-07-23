from typing import Any, Dict

from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.artifact import CalendarArtifact


class ICalendarProvider(IService):
    """
    Abstracts specific calendar backends (Google Calendar, Outlook) for the CalendarCapability.
    """
    def query_calendar(self, query: str) -> list[CalendarArtifact]:
        ...

    def create_event(self, details: Dict[str, Any]) -> CalendarArtifact:
        ...

    def move_event(self, event_id: str, new_time: str) -> CalendarArtifact:
        ...

    def delete_event(self, event_id: str) -> None:
        ...
