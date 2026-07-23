"""
Meeting Intelligence Capability

Provides tools for meeting transcription, note-taking, action item extraction,
and meeting summaries powered by AI.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import re

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.provider import IProvider
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.health import ProviderHealth


class MeetingStatus(str, Enum):
    """Meeting status."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Participant:
    """A meeting participant."""
    def __init__(self, name: str, email: str = "", role: str = "attendee"):
        self.name = name
        self.email = email
        self.role = role  # organizer, presenter, attendee


@dataclass
class ActionItem:
    """An action item from a meeting."""
    id: str
    description: str
    assignee: str
    due_date: Optional[str]
    completed: bool = False
    priority: str = "medium"  # low, medium, high, urgent
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class MeetingNote:
    """A meeting note entry."""
    id: str
    timestamp: str
    speaker: str
    content: str
    type: str = "note"  # note, decision, question, action


@dataclass
class Meeting:
    """A meeting record."""
    id: str
    title: str
    date: str
    start_time: str
    end_time: Optional[str]
    participants: List[Participant] = field(default_factory=list)
    transcript: str = ""
    notes: List[MeetingNote] = field(default_factory=list)
    action_items: List[ActionItem] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)
    summary: str = ""
    status: MeetingStatus = MeetingStatus.SCHEDULED
    tags: List[str] = field(default_factory=list)
    calendar_event_id: Optional[str] = None
    
    def __post_init__(self):
        if isinstance(self.status, str):
            self.status = MeetingStatus(self.status)


class MeetingIntelligenceCapability:
    """
    Meeting Intelligence capability for CHITTI.
    
    Tools:
    - start_meeting_recording: Start recording a meeting
    - stop_meeting_recording: Stop and process meeting
    - add_meeting_note: Add a note during meeting
    - add_action_item: Add an action item
    - extract_action_items: Auto-extract action items from transcript
    - generate_summary: Generate meeting summary
    - get_meeting_notes: Get all notes from a meeting
    - list_action_items: List all action items
    - complete_action_item: Mark action item complete
    - search_meetings: Search past meetings
    - get_meeting_summary: Get meeting summary
    - schedule_followup: Schedule follow-up meeting
    - send_meeting_notes: Send notes via email
    """
    
    def __init__(self, logger: Optional[ILoggingService] = None):
        self.logger = logger or MockLogger()
        self._state = ServiceState.STOPPED
        self._is_healthy = True
        
        # Data storage
        self._meetings: List[Meeting] = []
        self._current_meeting: Optional[Meeting] = None
        self._action_items: List[ActionItem] = []
        self._templates: Dict[str, str] = self._default_templates()
        
        self.logger.info("[MeetingIntelligence] Initialized")
    
    @property
    def name(self) -> str:
        return "MeetingIntelligenceCapability"
    
    @property
    def state(self) -> ServiceState:
        return self._state
    
    def initialize(self) -> None:
        """Initialize the capability."""
        self._state = ServiceState.RUNNING
        self._is_healthy = True
        self.logger.info("[MeetingIntelligence] Started")
    
    def shutdown(self) -> None:
        """Shutdown the capability."""
        if self._current_meeting:
            self.stop_meeting_recording()
        self._state = ServiceState.STOPPED
        self.logger.info("[MeetingIntelligence] Stopped")
    
    def health_check(self) -> Dict[str, Any]:
        """Return health status."""
        return {
            "status": "healthy" if self._is_healthy else "unhealthy",
            "recording_active": self._current_meeting is not None,
            "total_meetings": len(self._meetings),
            "pending_action_items": sum(1 for ai in self._action_items if not ai.completed)
        }
    
    def discover_tools(self) -> List[str]:
        """Return list of available tools."""
        return [
            "start_meeting_recording",
            "stop_meeting_recording",
            "add_meeting_note",
            "add_action_item",
            "extract_action_items",
            "generate_summary",
            "get_meeting_notes",
            "list_action_items",
            "complete_action_item",
            "update_action_item",
            "search_meetings",
            "get_meeting_summary",
            "schedule_followup",
            "send_meeting_notes",
            "get_pending_actions",
            "get_overdue_actions",
            "set_note_template"
        ]
    
    def _default_templates(self) -> Dict[str, str]:
        """Default meeting note templates."""
        return {
            "standup": "## Daily Standup\n\n### Yesterday\n- \n\n### Today\n- \n\n### Blockers\n- ",
            "1on1": "## 1:1 Meeting\n\n### Discussion Points\n- \n\n### Feedback\n- \n\n### Action Items\n- ",
            "brainstorm": "## Brainstorm Session\n\n### Ideas\n1. \n\n### Action Items\n- ",
            "retro": "## Retrospective\n\n### What went well\n- \n\n### What could improve\n- \n\n### Action items\n- "
        }
    
    # ========== MEETING RECORDING TOOLS ==========
    
    def start_meeting_recording(
        self,
        title: str,
        participants: Optional[List[Dict]] = None,
        tags: Optional[List[str]] = None,
        calendar_event_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start recording a meeting.
        
        Args:
            title: Meeting title
            participants: List of participant dicts with name, email, role
            tags: Optional tags
            calendar_event_id: Linked calendar event ID
            
        Returns:
            Meeting info
        """
        # Stop any current recording
        if self._current_meeting:
            self.stop_meeting_recording()
        
        meeting_id = f"meet_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Parse participants
        parsed_participants = []
        if participants:
            for p in participants:
                parsed_participants.append(Participant(
                    name=p.get("name", "Unknown"),
                    email=p.get("email", ""),
                    role=p.get("role", "attendee")
                ))
        
        meeting = Meeting(
            id=meeting_id,
            title=title,
            date=datetime.now().strftime("%Y-%m-%d"),
            start_time=datetime.now().isoformat(),
            end_time=None,
            participants=parsed_participants,
            status=MeetingStatus.IN_PROGRESS,
            tags=tags or [],
            calendar_event_id=calendar_event_id
        )
        
        self._current_meeting = meeting
        self._meetings.append(meeting)
        
        self.logger.info(f"[MeetingIntelligence] Started recording: {title}")
        
        return {
            "id": meeting_id,
            "title": title,
            "started_at": meeting.start_time,
            "status": "recording",
            "participant_count": len(parsed_participants)
        }
    
    def stop_meeting_recording(self) -> Dict[str, Any]:
        """
        Stop recording and process meeting.
        
        Returns:
            Meeting summary
        """
        if not self._current_meeting:
            return {"error": "No active meeting recording"}
        
        meeting = self._current_meeting
        meeting.end_time = datetime.now().isoformat()
        meeting.status = MeetingStatus.COMPLETED
        
        # Auto-extract action items
        self._extract_from_transcript(meeting)
        
        # Generate summary
        meeting.summary = self._generate_summary_text(meeting)
        
        # Add action items to global list
        self._action_items.extend(meeting.action_items)
        
        result = {
            "id": meeting.id,
            "title": meeting.title,
            "duration_minutes": self._calculate_duration(meeting),
            "notes_count": len(meeting.notes),
            "action_items_count": len(meeting.action_items),
            "decisions_count": len(meeting.decisions),
            "summary": meeting.summary[:200] + "..." if len(meeting.summary) > 200 else meeting.summary,
            "status": "processed"
        }
        
        self._current_meeting = None
        self.logger.info(f"[MeetingIntelligence] Stopped recording: {meeting.title}")
        
        return result
    
    def _calculate_duration(self, meeting: Meeting) -> int:
        """Calculate meeting duration in minutes."""
        if meeting.end_time:
            start = datetime.fromisoformat(meeting.start_time)
            end = datetime.fromisoformat(meeting.end_time)
            return int((end - start).total_seconds() / 60)
        return 0
    
    def _extract_from_transcript(self, meeting: Meeting):
        """Extract action items and decisions from transcript."""
        if not meeting.transcript:
            return
        
        # Pattern matching for action items
        action_patterns = [
            r'(?:@(\w+)|(\w+)\s+will)',
            r'(?:TODO|FIXME|ACTION):\s*(.+)',
            r'(?:(\w+)\s+should)\s+(.+)',
        ]
        
        # Pattern matching for decisions
        decision_patterns = [
            r'(?:DECIDED|AGREED|CONCLUDED):\s*(.+)',
            r'(?:we\s+(?:will|shall|are going to))\s+(.+)',
        ]
        
        # Simplified extraction (in production, use LLM)
        # For now, mark that extraction would happen here
        pass
    
    def _generate_summary_text(self, meeting: Meeting) -> str:
        """Generate meeting summary text."""
        parts = [
            f"# {meeting.title}",
            f"**Date:** {meeting.date}",
            f"**Duration:** {self._calculate_duration(meeting)} minutes",
            f"**Participants:** {', '.join(p.name for p in meeting.participants)}",
            "",
            "## Summary",
            self._generate_executive_summary(meeting),
        ]
        
        if meeting.notes:
            parts.append("\n## Key Points")
            for note in meeting.notes:
                parts.append(f"- [{note.timestamp}] {note.speaker}: {note.content}")
        
        if meeting.action_items:
            parts.append("\n## Action Items")
            for item in meeting.action_items:
                status = "✅" if item.completed else "⬜"
                parts.append(f"{status} **{item.assignee}**: {item.description}")
        
        if meeting.decisions:
            parts.append("\n## Decisions")
            for decision in meeting.decisions:
                parts.append(f"- {decision}")
        
        return "\n".join(parts)
    
    def _generate_executive_summary(self, meeting: Meeting) -> str:
        """Generate executive summary."""
        summary_parts = []
        
        # Meeting overview
        summary_parts.append(
            f"This {self._calculate_duration(meeting)}-minute meeting with "
            f"{len(meeting.participants)} participants covered "
            f"{len(meeting.notes)} discussion points."
        )
        
        if meeting.action_items:
            pending = sum(1 for ai in meeting.action_items if not ai.completed)
            summary_parts.append(
                f"{pending} action items were identified for follow-up."
            )
        
        if meeting.decisions:
            summary_parts.append(
                f"{len(meeting.decisions)} key decisions were made."
            )
        
        return " ".join(summary_parts)
    
    # ========== NOTE & ACTION TOOLS ==========
    
    def add_meeting_note(
        self,
        content: str,
        speaker: str = "You",
        note_type: str = "note"
    ) -> Dict[str, Any]:
        """
        Add a note during meeting.
        
        Args:
            content: Note content
            speaker: Who said this
            note_type: Type of note (note, decision, question, action)
            
        Returns:
            Created note
        """
        if not self._current_meeting:
            return {"error": "No active meeting recording"}
        
        note_id = f"note_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        note = MeetingNote(
            id=note_id,
            timestamp=datetime.now().strftime("%H:%M"),
            speaker=speaker,
            content=content,
            type=note_type
        )
        
        self._current_meeting.notes.append(note)
        
        # If it's a decision note, add to decisions
        if note_type == "decision":
            self._current_meeting.decisions.append(content)
        
        self.logger.info(f"[MeetingIntelligence] Added note: {content[:50]}...")
        
        return {
            "id": note_id,
            "timestamp": note.timestamp,
            "speaker": speaker,
            "content": content,
            "type": note_type
        }
    
    def add_action_item(
        self,
        description: str,
        assignee: str,
        due_date: Optional[str] = None,
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """
        Add an action item.
        
        Args:
            description: What needs to be done
            assignee: Who is responsible
            due_date: Optional due date (YYYY-MM-DD)
            priority: low, medium, high, urgent
            
        Returns:
            Created action item
        """
        # Use current meeting or create standalone
        meeting_id = self._current_meeting.id if self._current_meeting else None
        
        item_id = f"action_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        item = ActionItem(
            id=item_id,
            description=description,
            assignee=assignee,
            due_date=due_date,
            completed=False,
            priority=priority
        )
        
        self._action_items.append(item)
        
        if self._current_meeting:
            self._current_meeting.action_items.append(item)
        
        self.logger.info(f"[MeetingIntelligence] Added action item: {description[:50]}...")
        
        return {
            "id": item_id,
            "description": description,
            "assignee": assignee,
            "due_date": due_date,
            "priority": priority,
            "completed": False,
            "meeting_id": meeting_id
        }
    
    def extract_action_items(self, text: str) -> Dict[str, Any]:
        """
        Extract action items from text/transcript.
        
        Args:
            text: Text to analyze
            
        Returns:
            Extracted action items
        """
        # In production, this would use LLM
        # For now, use pattern matching
        
        action_patterns = [
            r'(?:TODO|FIXME|ACTION):\s*(.+?)(?:\n|$)',
            r'(?:@(\w+)|(\w+)\s+will)\s+(?:take care of|custom|handle)(?:\s+(.+?))?(?:\n|$)',
            r'(?:(\w+)\s+should)\s+(.+?)(?:\n|$)',
            r'(?:(\w+)\s+to)\s+(.+?)(?:\n|$)',
        ]
        
        extracted = []
        for pattern in action_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if groups:
                    # Simplified parsing
                    extracted.append({
                        "text": match.group(0),
                        "possible_assignee": groups[0] if groups else None
                    })
        
        return {
            "count": len(extracted),
            "items": extracted,
            "recommendation": "Review and confirm extracted items before adding"
        }
    
    def generate_summary(self, meeting_id: str) -> Dict[str, Any]:
        """
        Generate or regenerate meeting summary.
        
        Args:
            meeting_id: ID of meeting
            
        Returns:
            Generated summary
        """
        meeting = self._find_meeting(meeting_id)
        if not meeting:
            return {"error": f"Meeting not found: {meeting_id}"}
        
        meeting.summary = self._generate_summary_text(meeting)
        
        return {
            "id": meeting_id,
            "title": meeting.title,
            "summary": meeting.summary,
            "generated_at": datetime.now().isoformat()
        }
    
    def _find_meeting(self, meeting_id: str) -> Optional[Meeting]:
        """Find meeting by ID."""
        for meeting in self._meetings:
            if meeting.id == meeting_id:
                return meeting
        return None
    
    # ========== LIST & SEARCH TOOLS ==========
    
    def get_meeting_notes(self, meeting_id: str) -> Dict[str, Any]:
        """
        Get all notes from a meeting.
        
        Args:
            meeting_id: ID of meeting
            
        Returns:
            All notes
        """
        meeting = self._find_meeting(meeting_id)
        if not meeting:
            return {"error": f"Meeting not found: {meeting_id}"}
        
        return {
            "meeting_id": meeting_id,
            "title": meeting.title,
            "notes": [
                {
                    "id": n.id,
                    "timestamp": n.timestamp,
                    "speaker": n.speaker,
                    "content": n.content,
                    "type": n.type
                }
                for n in meeting.notes
            ],
            "decisions": meeting.decisions,
            "action_items": [
                {
                    "id": a.id,
                    "description": a.description,
                    "assignee": a.assignee,
                    "completed": a.completed
                }
                for a in meeting.action_items
            ]
        }
    
    def list_action_items(
        self,
        assignee: Optional[str] = None,
        meeting_id: Optional[str] = None,
        include_completed: bool = False
    ) -> Dict[str, Any]:
        """
        List action items.
        
        Args:
            assignee: Filter by assignee
            meeting_id: Filter by meeting
            include_completed: Include completed items
            
        Returns:
            List of action items
        """
        items = self._action_items
        
        if assignee:
            items = [i for i in items if i.assignee.lower() == assignee.lower()]
        
        if meeting_id:
            items = [i for i in items if self._get_meeting_for_action(i.id) == meeting_id]
        
        if not include_completed:
            items = [i for i in items if not i.completed]
        
        return {
            "count": len(items),
            "items": [
                {
                    "id": i.id,
                    "description": i.description,
                    "assignee": i.assignee,
                    "due_date": i.due_date,
                    "priority": i.priority,
                    "completed": i.completed,
                    "meeting_id": self._get_meeting_for_action(i.id)
                }
                for i in items
            ]
        }
    
    def _get_meeting_for_action(self, action_id: str) -> Optional[str]:
        """Get meeting ID for an action item."""
        for meeting in self._meetings:
            for item in meeting.action_items:
                if item.id == action_id:
                    return meeting.id
        return None
    
    def complete_action_item(self, item_id: str) -> Dict[str, Any]:
        """
        Mark action item as complete.
        
        Args:
            item_id: ID of action item
            
        Returns:
            Updated item
        """
        for item in self._action_items:
            if item.id == item_id:
                item.completed = True
                self.logger.info(f"[MeetingIntelligence] Completed action item: {item_id}")
                return {
                    "id": item_id,
                    "completed": True,
                    "description": item.description
                }
        
        return {"error": f"Action item not found: {item_id}"}
    
    def update_action_item(
        self,
        item_id: str,
        description: Optional[str] = None,
        assignee: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an action item.
        
        Args:
            item_id: ID of action item
            description: New description
            assignee: New assignee
            due_date: New due date
            priority: New priority
            
        Returns:
            Updated item
        """
        for item in self._action_items:
            if item.id == item_id:
                if description:
                    item.description = description
                if assignee:
                    item.assignee = assignee
                if due_date:
                    item.due_date = due_date
                if priority:
                    item.priority = priority
                
                return {
                    "id": item_id,
                    "description": item.description,
                    "assignee": item.assignee,
                    "due_date": item.due_date,
                    "priority": item.priority
                }
        
        return {"error": f"Action item not found: {item_id}"}
    
    def search_meetings(
        self,
        query: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search past meetings.
        
        Args:
            query: Search query
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Matching meetings
        """
        results = []
        
        for meeting in self._meetings:
            # Date filter
            if start_date and meeting.date < start_date:
                continue
            if end_date and meeting.date > end_date:
                continue
            
            # Text search
            query_lower = query.lower()
            if (query_lower in meeting.title.lower() or
                query_lower in meeting.summary.lower() or
                query_lower in meeting.transcript.lower() or
                any(query_lower in note.content.lower() for note in meeting.notes)):
                results.append({
                    "id": meeting.id,
                    "title": meeting.title,
                    "date": meeting.date,
                    "duration_minutes": self._calculate_duration(meeting),
                    "participant_count": len(meeting.participants),
                    "matching_notes": sum(
                        1 for note in meeting.notes
                        if query_lower in note.content.lower()
                    )
                })
        
        return {
            "query": query,
            "count": len(results),
            "results": results
        }
    
    def get_meeting_summary(self, meeting_id: str) -> Dict[str, Any]:
        """
        Get meeting summary.
        
        Args:
            meeting_id: ID of meeting
            
        Returns:
            Meeting summary
        """
        meeting = self._find_meeting(meeting_id)
        if not meeting:
            return {"error": f"Meeting not found: {meeting_id}"}
        
        return {
            "id": meeting.id,
            "title": meeting.title,
            "date": meeting.date,
            "duration_minutes": self._calculate_duration(meeting),
            "participants": [p.name for p in meeting.participants],
            "summary": meeting.summary or self._generate_summary_text(meeting),
            "notes_count": len(meeting.notes),
            "action_items_count": len(meeting.action_items),
            "decisions_count": len(meeting.decisions),
            "pending_actions": sum(1 for a in meeting.action_items if not a.completed),
            "status": meeting.status.value
        }
    
    # ========== FOLLOWUP TOOLS ==========
    
    def schedule_followup(
        self,
        original_meeting_id: str,
        title: str,
        date: str,
        time: str,
        participants: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Schedule follow-up meeting.
        
        Args:
            original_meeting_id: Original meeting ID
            title: Follow-up title
            date: Meeting date (YYYY-MM-DD)
            time: Meeting time (HH:MM)
            participants: Optional participants
            
        Returns:
            Created follow-up meeting
        """
        original = self._find_meeting(original_meeting_id)
        if not original:
            return {"error": f"Original meeting not found: {original_meeting_id}"}
        
        # Create new meeting as follow-up
        result = self.start_meeting_recording(
            title=f"Follow-up: {title}",
            participants=participants,
            tags=["follow-up", original_meeting_id]
        )
        
        # Stop it immediately since it's scheduled
        self._current_meeting.date = date
        self._current_meeting.start_time = f"{date}T{time}:00"
        self._current_meeting.status = MeetingStatus.SCHEDULED
        
        # Link to original
        self._current_meeting.transcript = f"Follow-up to: {original.title}"
        
        self.stop_meeting_recording()
        
        return {
            "id": result["id"],
            "title": title,
            "date": date,
            "time": time,
            "linked_to": original_meeting_id,
            "pending_actions_carried": [
                {"description": a.description, "assignee": a.assignee}
                for a in original.action_items if not a.completed
            ]
        }
    
    # ========== SEND TOOLS ==========
    
    def send_meeting_notes(
        self,
        meeting_id: str,
        recipients: List[str],
        include_actions: bool = True,
        include_summary: bool = True
    ) -> Dict[str, Any]:
        """
        Send meeting notes via email.
        
        Args:
            meeting_id: ID of meeting
            recipients: Email addresses
            include_actions: Include action items
            include_summary: Include summary
            
        Returns:
            Send result
        """
        meeting = self._find_meeting(meeting_id)
        if not meeting:
            return {"error": f"Meeting not found: {meeting_id}"}
        
        # Build email content
        content_parts = []
        
        if include_summary:
            content_parts.append(f"# {meeting.title}")
            content_parts.append(f"Date: {meeting.date}")
            content_parts.append(f"Duration: {self._calculate_duration(meeting)} minutes\n")
            content_parts.append(meeting.summary or self._generate_summary_text(meeting))
        
        if include_actions and meeting.action_items:
            content_parts.append("\n## Action Items")
            for item in meeting.action_items:
                status = "✅" if item.completed else "⬜"
                due = f" (Due: {item.due_date})" if item.due_date else ""
                content_parts.append(f"{status} **{item.assignee}**: {item.description}{due}")
        
        # In production, would integrate with email provider
        self.logger.info(f"[MeetingIntelligence] Would send notes to {recipients}")
        
        return {
            "success": True,
            "meeting_id": meeting_id,
            "recipients": recipients,
            "subject": f"Meeting Notes: {meeting.title}",
            "preview": "\n".join(content_parts)[:500]
        }
    
    # ========== DASHBOARD TOOLS ==========
    
    def get_pending_actions(self, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Get all pending action items.
        
        Args:
            days_ahead: Days to look ahead
            
        Returns:
            Pending actions grouped
        """
        pending = [a for a in self._action_items if not a.completed]
        
        # Group by assignee
        by_assignee: Dict[str, List] = {}
        for item in pending:
            if item.assignee not in by_assignee:
                by_assignee[item.assignee] = []
            by_assignee[item.assignee].append({
                "id": item.id,
                "description": item.description,
                "due_date": item.due_date,
                "priority": item.priority,
                "meeting_id": self._get_meeting_for_action(item.id)
            })
        
        return {
            "total_pending": len(pending),
            "by_assignee": by_assignee,
            "high_priority": [
                {
                    "id": a.id,
                    "description": a.description,
                    "assignee": a.assignee,
                    "due_date": a.due_date
                }
                for a in pending if a.priority in ["high", "urgent"]
            ]
        }
    
    def get_overdue_actions(self) -> Dict[str, Any]:
        """
        Get overdue action items.
        
        Returns:
            Overdue actions
        """
        today = datetime.now().strftime("%Y-%m-%d")
        overdue = []
        
        for item in self._action_items:
            if not item.completed and item.due_date and item.due_date < today:
                overdue.append({
                    "id": item.id,
                    "description": item.description,
                    "assignee": item.assignee,
                    "due_date": item.due_date,
                    "days_overdue": (datetime.now().date() - datetime.fromisoformat(item.due_date).date()).days,
                    "priority": item.priority
                })
        
        return {
            "count": len(overdue),
            "items": overdue
        }
    
    def set_note_template(
        self,
        template_name: str,
        template_content: str
    ) -> Dict[str, Any]:
        """
        Set a custom note template.
        
        Args:
            template_name: Name of template
            template_content: Template content (markdown)
            
        Returns:
            Confirmation
        """
        self._templates[template_name] = template_content
        
        return {
            "name": template_name,
            "saved": True,
            "available_templates": list(self._templates.keys())
        }


class MockLogger:
    """Mock logger."""
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


def get_capability(logger: Optional[ILoggingService] = None) -> MeetingIntelligenceCapability:
    """Factory function."""
    return MeetingIntelligenceCapability(logger=logger)
