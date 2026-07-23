import os
from typing import Any, Dict, List
import datetime

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.mail_provider import IMailProvider
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.artifact import EmailArtifact

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    Credentials = None
    build = None


class GmailProvider(IMailProvider):
    """
    Gmail provider that fetches emails using the Google API.
    Fails gracefully if credentials are missing or the API client is not installed.
    """
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED
        self._service = None

        # Credentials path (managed by First Run Wizard)
        local_app_data = os.getenv("LOCALAPPDATA", os.path.expanduser("~"))
        chitti_dir = os.path.join(local_app_data, "CHITTI")
        self.credentials_path = os.path.join(chitti_dir, "credentials", "credentials.json")
        self.token_path = os.path.join(chitti_dir, "tokens", "gmail_token.json")

    @property
    def name(self) -> str:
        return "GmailProvider"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        if build is None:
            self.logger.warning("google-api-python-client is not installed. Gmail will be offline.")
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
                    self.logger.warning(f"Failed to refresh Gmail token: {e}")
                    creds = None

        if creds and creds.valid:
            try:
                self._service = build("gmail", "v1", credentials=creds)
                self._state = ServiceState.RUNNING
                self.logger.info(f"{self.name} initialized successfully.")
            except Exception as e:
                self.logger.warning(f"Failed to build Gmail service: {e}")
                self._state = ServiceState.ERROR
        else:
            self.logger.warning("Gmail token is missing or invalid. GmailProvider will degrade gracefully.")
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
        self.logger.info("GmailProvider attempting recovery...")
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

    def query_mail(self, query: str) -> List[EmailArtifact]:
        if self._state != ServiceState.RUNNING or not self._service:
            self.logger.info("GmailProvider is degraded, skipping query.")
            return []

        artifacts = []
        try:
            # query example: 'is:unread label:important'
            results = self._service.users().messages().list(userId="me", q=query, maxResults=5).execute()
            messages = results.get("messages", [])

            for msg in messages:
                msg_data = self._service.users().messages().get(userId="me", id=msg["id"]).execute()
                headers = msg_data["payload"]["headers"]
                subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
                sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
                snippet = msg_data.get("snippet", "")

                artifact = EmailArtifact(
                    source=self.name,
                    capability="MailCapability",
                    metadata={"subject": subject, "sender": sender, "id": msg["id"]},
                    content=snippet
                )
                artifacts.append(artifact)
        except Exception as e:
            self.logger.warning(f"Error querying Gmail: {e}")

        return artifacts

    def reply(self, email_id: str, content: str) -> EmailArtifact:
        self.logger.info(f"GmailProvider: Mock reply sent to email_id {email_id}.")
        return EmailArtifact(
            source=self.name,
            capability="MailCapability",
            metadata={"id": email_id, "action": "reply"},
            content=content
        )

    def archive(self, email_id: str) -> None:
        self.logger.info(f"GmailProvider: Mock archived email_id {email_id}.")
