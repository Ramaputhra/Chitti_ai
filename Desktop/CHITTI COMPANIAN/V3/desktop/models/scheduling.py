import uuid
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

class TriggerType(Enum):
    TIME = "TIME"
    EVENT = "EVENT"
    CONDITION = "CONDITION"

class EventSource(Enum):
    VOICE = "VOICE"
    CHAT = "CHAT"
    SYSTEM = "SYSTEM"
    WORKFLOW = "WORKFLOW"
    PLUGIN = "PLUGIN"
    USER_INTERFACE = "USER_INTERFACE"
    RECOVERED_AFTER_REBOOT = "RECOVERED_AFTER_REBOOT"

class EventOwner(Enum):
    USER = "USER"
    SYSTEM = "SYSTEM"
    PLUGIN = "PLUGIN"

class EventCondition(Enum):
    COPY_FINISHED = "COPY_FINISHED"
    DOWNLOAD_FINISHED = "DOWNLOAD_FINISHED"
    PROCESS_EXIT = "PROCESS_EXIT"
    BATTERY_LEVEL = "BATTERY_LEVEL"
    NETWORK_AVAILABLE = "NETWORK_AVAILABLE"
    USB_CONNECTED = "USB_CONNECTED"
    CUSTOM = "CUSTOM"

class RetryPolicy(Enum):
    NEVER = "NEVER"
    ONCE = "ONCE"
    UNTIL_SUCCESS = "UNTIL_SUCCESS"
    CUSTOM = "CUSTOM"

class EventResolution(Enum):
    COMPLETED = "COMPLETED"
    SNOOZED = "SNOOZED"
    DISMISSED = "DISMISSED"
    RESCHEDULED = "RESCHEDULED"
    IGNORED = "IGNORED"
    EXPIRED = "EXPIRED"

class EventPriority(Enum):
    CRITICAL = 4
    HIGH = 3
    NORMAL = 2
    LOW = 1

class EventRecurrence(Enum):
    ONE_TIME = "ONE_TIME"
    DAILY = "DAILY"
    WEEKDAYS = "WEEKDAYS"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    CUSTOM = "CUSTOM"

class EventStatus(Enum):
    CREATED = "CREATED"
    SCHEDULED = "SCHEDULED"
    WAITING = "WAITING"
    TRIGGERED = "TRIGGERED"
    FOLLOW_UP = "FOLLOW_UP"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"

@dataclass
class ScheduledEvent:
    """
    The unified waiting mechanism for CHITTI (Temporal Rule).
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trigger_type: TriggerType = TriggerType.TIME
    
    # If TIME trigger
    trigger_time: Optional[float] = None
    
    # If CONDITION trigger
    condition: Optional[EventCondition] = None
    
    label: str = "Unnamed Event"
    payload_type: str = "Reminder" # "Reminder", "Timer", "Monitoring", "Timetable Plan"
    payload_data: Dict[str, Any] = field(default_factory=dict)
    
    status: EventStatus = EventStatus.CREATED
    priority: EventPriority = EventPriority.NORMAL
    recurrence: EventRecurrence = EventRecurrence.ONE_TIME
    
    source: EventSource = EventSource.SYSTEM
    owner: EventOwner = EventOwner.USER
    retry_policy: RetryPolicy = RetryPolicy.NEVER
    
    resolution: Optional[EventResolution] = None
    
    created_at: float = field(default_factory=datetime.now().timestamp)
    updated_at: float = field(default_factory=datetime.now().timestamp)
    completed_at: Optional[float] = None
    
    confidence: float = 100.0
    origin_intent: Optional[str] = None
