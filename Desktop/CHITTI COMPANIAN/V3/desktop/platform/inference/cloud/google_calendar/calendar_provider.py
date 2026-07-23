import os
from typing import Any, Dict, List
import datetime

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.calendar_provider import ICalendarProvider
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.artifact import CalendarArtifact

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    Credentials = None
    build = None


class GoogleCalendarProvider(ICalendarProvider):
    """
    Google Calendar provider that fetches events using the Google API.
    Fails gracefully if credentials are missing or the API client is not installed.
    """
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED
        self._service = None

        # Credentials path (managed by First Run Wizard)
        local_app_data = os.getenv("LOCALAPPDATA", os.path.expanduser("~"))
        chitti_dir = os.path.join(local_app_data, "CHITTI")
        self.credentials_path = os.path.join(chitti_dir, "credentials", "credentials.json")
        self.token_path = os.path.join(chitti_dir, "tokens", "calendar_token.json")

    @property
    def name(self) -> str:
        return "GoogleCalendarProvider"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        if build is None:
            self.logger.warning("google-api-python-client is not installed. Calendar will be offline.")
            self._state = ServiceState.ERROR
            return

        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.warning(f"Failed to refresh Calendar token: {e}")
                    creds = None

        if creds and creds.valid:
            try:
                self._service = build("calendar", "v3", credentials=creds)
                self._state = ServiceState.RUNNING
                self.logger.info(f"{self.name} initialized successfully.")
            except Exception as e:
                self.logger.warning(f"Failed to build Calendar service: {e}")
                self._state = ServiceState.ERROR
        else:
            self.logger.warning("Calendar token missing. GoogleCalendarProvider will degrade gracefully.")
            self._state = ServiceState.STOPPED

    def start(self) -> None:
        if self._state == ServiceState.STOPPED and self._service:
            self._state = ServiceState.RUNNING

    def pause(self) -> None:
        self._state = ServiceState.STOPPED

    def resume(self) -> None:
        if self._service:
            self._state = ServiceState.RUNNING

    def recover(self) -> None:
        self.logger.info("GoogleCalendarProvider attempting recovery...")
        self.shutdown()
        self.initialize()
        self.start()

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {
            "authenticated": self._service is not None,
            "token_exists": os.path.exists(self.token_path)
        }

    def query_calendar(self, query: str) -> List[CalendarArtifact]:
        if self._state != ServiceState.RUNNING or not self._service:
            self.logger.info("GoogleCalendarProvider is not running, skipping query.")
            return []

        artifacts = []
        try:
            # Simplified: just fetch today's events if query == 'today'
            now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
            end_of_day = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat() + "Z"

            events_result = self._service.events().list(
                calendarId="primary", timeMin=now, timeMax=end_of_day,
                maxResults=10, singleEvents=True, orderBy="startTime"
            ).execute()
            events = events_result.get("items", [])

            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                summary = event.get("summary", "Untitled Event")
                
                artifact = CalendarArtifact(
                    source=self.name,
                    capability="CalendarCapability",
                    metadata={"start_time": start, "id": event["id"]},
                    content=summary
                )
                artifacts.append(artifact)
        except Exception as e:
            self.logger.warning(f"Error querying Google Calendar: {e}")

        return artifacts

    def create_event(self, details: Dict[str, Any]) -> CalendarArtifact:
        raise NotImplementedError("create_event not implemented yet.")

    def move_event(self, event_id: str, new_time: str) -> CalendarArtifact:
        raise NotImplementedError("move_event not implemented yet.")
