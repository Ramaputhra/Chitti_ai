from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class Contact:
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]

@dataclass
class Recipient:
    contact: Contact
    recipient_type: str # to, cc, bcc

@dataclass
class Attachment:
    filename: str
    size_bytes: int
    mime_type: str
    url: Optional[str] = None
    data: Optional[bytes] = None

@dataclass
class EmailMessage:
    message_id: str
    subject: str
    sender: Contact
    recipients: List[Recipient]
    body_text: str
    body_html: Optional[str]
    attachments: List[Attachment]
    timestamp: datetime
    is_read: bool

@dataclass
class CalendarEvent:
    event_id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    organizer: Contact
    attendees: List[Recipient]
    location: Optional[str]
    is_all_day: bool

@dataclass
class Reminder:
    reminder_id: str
    title: str
    trigger_time: datetime
    is_completed: bool

@dataclass
class Notification:
    notification_id: str
    title: str
    message: str
    source_app: str
    timestamp: datetime
    is_dismissed: bool
    priority: str # low, normal, high

@dataclass
class ApiResponse:
    status_code: int
    headers: Dict[str, str]
    body: Any
    latency_ms: int
