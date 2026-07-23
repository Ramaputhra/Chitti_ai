from typing import Any, Dict, List
import datetime
from googleapiclient.discovery import build

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.provider import IProvider
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.health import ProviderHealth
from desktop.runtime.authentication.google_identity import GoogleIdentity


class CalendarProvider(IProvider):
    """
    Real Google Calendar API provider. Relies on GoogleIdentity for auth.
    """
    def __init__(self, google_identity: GoogleIdentity, logger: ILoggingService) -> None:
        self.google_identity = google_identity
        self.logger = logger
        self._state = ServiceState.STOPPED
        self._is_healthy = False

    @property
    def name(self) -> str: return "CalendarProvider"

    @property
    def state(self) -> ServiceState: return self._state

    def initialize(self) -> None:
        self.logger.info("Initializing Calendar Provider...")
        creds = self.google_identity.get_credentials()
        if creds and creds.valid:
            self._is_healthy = True
            self._state = ServiceState.RUNNING
            self.logger.info("Calendar initialized successfully.")
        else:
            self.logger.warning("Calendar lacks valid Google credentials. Unavailable.")
            self._is_healthy = False

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def get_provider_health(self) -> ProviderHealth:
        return ProviderHealth(
            status="Healthy" if self._is_healthy else "Unavailable",
            healthy=self._is_healthy,
            enabled=True,
            configured=True,
            authenticated=self._is_healthy,
            latency_ms=500,
            last_error=None,
            version="1.0.0",
            model="Calendar API",
            uptime=0
        )

    def health_check(self) -> Dict[str, Any]:
        h = self.get_provider_health()
        return {"status": h.status}

    def benchmark(self) -> Dict[str, Any]:
        return {"latency_ms": 500}

    def capabilities(self) -> List[str]:
        return ["read_events", "create_events"]

    def version(self) -> str:
        return "1.0.0"

    def configuration(self) -> Dict[str, Any]:
        return {}

    def get_upcoming_meetings(self, time_range: str = "today") -> List[Dict[str, Any]]:
        if not self._is_healthy: return []
            
        creds = self.google_identity.get_credentials()
        if not creds: return []
            
        self.logger.info(f"Fetching upcoming meetings for {time_range}")
        try:
            service = build("calendar", "v3", credentials=creds)
            now = datetime.datetime.utcnow().isoformat() + "Z"
            events_result = service.events().list(
                calendarId="primary", timeMin=now,
                maxResults=5, singleEvents=True,
                orderBy="startTime").execute()
            events = events_result.get("items", [])
            output = []
            for e in events:
                start = e["start"].get("dateTime", e["start"].get("date"))
                attendees = [a["email"] for a in e.get("attendees", [])]
                output.append({"title": e.get("summary", "Busy"), "attendees": attendees, "time": start})
            return output
        except Exception as e:
            self.logger.error(f"Calendar fetch failed: {e}")
            return []
