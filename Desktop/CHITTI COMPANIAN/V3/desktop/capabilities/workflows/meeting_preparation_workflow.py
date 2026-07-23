from typing import Any, Dict

from desktop.capabilities.communications.calendar_provider import CalendarProvider
from desktop.capabilities.communications.gmail_provider import GmailProvider
from desktop.capabilities.files.file_organization_capability import FileOrganizationCapability
from desktop.capabilities.notes.notes_capability import NotesCapability
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import IService, ServiceState


class MeetingPreparationWorkflow(IService):
    """
    The flagship hero capability for CP5.
    Orchestrates across all other CP5 capabilities to deliver a cohesive, end-to-end product experience.
    """
    def __init__(
        self,
        calendar: CalendarProvider,
        gmail: GmailProvider,
        notes: NotesCapability,
        files: FileOrganizationCapability,
        logger: ILoggingService
    ) -> None:
        self.calendar = calendar
        self.gmail = gmail
        self.notes = notes
        self.files = files
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str: return "MeetingPreparationWorkflow"

    @property
    def state(self) -> ServiceState: return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> Dict[str, Any]:
        return {"status": "Healthy"}

    def prepare_for_next_meeting(self) -> Dict[str, Any]:
        self.logger.info("Executing MeetingPreparationWorkflow...")
        
        # 1. Get next meeting from Calendar
        meetings = self.calendar.get_upcoming_meetings()
        if not meetings:
            return {"status": "no_meetings"}
        next_meeting = meetings[0]
        attendees = next_meeting.get("attendees", [])
        
        # 2. Fetch recent emails related to attendees
        emails = []
        for attendee in attendees:
            emails.extend(self.gmail.fetch_recent_emails(query=f"from:{attendee}"))
            
        # 3. Pull relevant semantic notes
        # In a real impl, this would query the semantic runtime for the meeting topic
        
        # 4. Generate summary (delegated to Planner/LLM in reality)
        summary = f"You have {next_meeting['title']} at {next_meeting['time']}. There are {len(emails)} unread emails from attendees."
        
        return {
            "status": "success",
            "meeting": next_meeting,
            "emails_reviewed": len(emails),
            "briefing": summary
        }
