"""
Reminder and Alert System Capability

Provides:
- Timed reminders
- Recurring alarms
- Persistent notifications
- Snooze functionality
- Priority levels
"""
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import uuid
import json
import os

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.event_bus import IEventBus, Event
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.ai import ToolInvocation

logger = logging.getLogger(__name__)


class ReminderPriority(str, Enum):
    """Priority levels for reminders."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ReminderStatus(str, Enum):
    """Status of a reminder."""
    PENDING = "pending"
    ACTIVE = "active"
    SNOOZED = "snoozed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class RecurrenceType(str, Enum):
    """Types of recurrence."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


@dataclass
class Reminder:
    """A reminder or alarm."""
    id: str
    title: str
    message: str
    priority: ReminderPriority
    status: ReminderStatus
    created_at: datetime
    scheduled_at: datetime
    recurrence: RecurrenceType
    recurrence_rule: Optional[str] = None
    snoozed_until: Optional[datetime] = None
    snooze_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "scheduled_at": self.scheduled_at.isoformat(),
            "recurrence": self.recurrence.value,
            "recurrence_rule": self.recurrence_rule,
            "snoozed_until": self.snoozed_until.isoformat() if self.snoozed_until else None,
            "snooze_count": self.snooze_count,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reminder':
        return cls(
            id=data["id"],
            title=data["title"],
            message=data["message"],
            priority=ReminderPriority(data.get("priority", "normal")),
            status=ReminderStatus(data.get("status", "pending")),
            created_at=datetime.fromisoformat(data["created_at"]),
            scheduled_at=datetime.fromisoformat(data["scheduled_at"]),
            recurrence=RecurrenceType(data.get("recurrence", "none")),
            recurrence_rule=data.get("recurrence_rule"),
            snoozed_until=datetime.fromisoformat(data["snoozed_until"]) if data.get("snoozed_until") else None,
            snooze_count=data.get("snooze_count", 0),
            metadata=data.get("metadata", {})
        )


class ReminderTriggeredEvent(Event):
    """Event fired when a reminder is triggered."""
    def __init__(self, reminder: Reminder):
        self.reminder = reminder
        self.event_type = "ReminderTriggered"


@dataclass
class ReminderStorage:
    """Persistent storage for reminders."""
    reminders: List[Dict[str, Any]] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)


class ReminderCapability(ICapability):
    """
    Reminder and Alert System Capability.
    Manages timed reminders, recurring alarms, and notifications.
    """
    
    def __init__(
        self,
        event_bus: Optional[IEventBus] = None,
        storage_path: str = "storage/reminders.json"
    ):
        self._state = ServiceState.STOPPED
        self._event_bus = event_bus
        self._storage_path = storage_path
        self._reminders: Dict[str, Reminder] = {}
        self._active_timers: Dict[str, asyncio.Task] = {}
        self._notification_callback: Optional[Callable] = None
        self._check_interval = 1.0  # Check every second
        self._storage = ReminderStorage()
        
        self._load()
    
    @property
    def name(self) -> str:
        return "ReminderCapability"
    
    @property
    def state(self) -> ServiceState:
        return self._state
    
    def initialize(self) -> None:
        """Initialize the capability."""
        self._state = ServiceState.RUNNING
        self._start_monitor()
        logger.info("ReminderCapability initialized")
    
    def shutdown(self) -> None:
        """Shutdown the capability."""
        self._stop_monitor()
        self._save()
        self._state = ServiceState.STOPPED
        logger.info("ReminderCapability shutdown")
    
    def set_notification_callback(self, callback: Callable[[Reminder], None]) -> None:
        """Set a callback for notification handling."""
        self._notification_callback = callback
    
    def discover_tools(self) -> List[ToolDescriptor]:
        """Return available tools."""
        return [
            ToolDescriptor(
                name="create_reminder",
                description="Create a new reminder or alarm",
                parameters=[
                    ToolParameter(name="title", type="string", required=True,
                                 description="Title of the reminder"),
                    ToolParameter(name="message", type="string", required=True,
                                 description="Message or description"),
                    ToolParameter(name="scheduled_at", type="string", required=True,
                                 description="ISO datetime when to trigger"),
                    ToolParameter(name="priority", type="string", required=False,
                                 description="Priority: low, normal, high, urgent"),
                    ToolParameter(name="recurrence", type="string", required=False,
                                 description="Recurrence: none, daily, weekly, monthly, yearly")
                ]
            ),
            ToolDescriptor(
                name="list_reminders",
                description="List all reminders",
                parameters=[
                    ToolParameter(name="status", type="string", required=False,
                                 description="Filter by status: pending, active, completed, cancelled")
                ]
            ),
            ToolDescriptor(
                name="get_reminder",
                description="Get details of a specific reminder",
                parameters=[
                    ToolParameter(name="reminder_id", type="string", required=True,
                                 description="ID of the reminder")
                ]
            ),
            ToolDescriptor(
                name="snooze_reminder",
                description="Snooze a reminder",
                parameters=[
                    ToolParameter(name="reminder_id", type="string", required=True,
                                 description="ID of the reminder"),
                    ToolParameter(name="minutes", type="integer", required=False,
                                 description="Minutes to snooze (default: 5)")
                ]
            ),
            ToolDescriptor(
                name="complete_reminder",
                description="Mark a reminder as completed",
                parameters=[
                    ToolParameter(name="reminder_id", type="string", required=True,
                                 description="ID of the reminder")
                ]
            ),
            ToolDescriptor(
                name="cancel_reminder",
                description="Cancel a reminder",
                parameters=[
                    ToolParameter(name="reminder_id", type="string", required=True,
                                 description="ID of the reminder")
                ]
            ),
            ToolDescriptor(
                name="update_reminder",
                description="Update a reminder",
                parameters=[
                    ToolParameter(name="reminder_id", type="string", required=True,
                                 description="ID of the reminder"),
                    ToolParameter(name="title", type="string", required=False,
                                 description="New title for the reminder"),
                    ToolParameter(name="message", type="string", required=False,
                                 description="New message for the reminder"),
                    ToolParameter(name="scheduled_at", type="string", required=False,
                                 description="New scheduled time (ISO format)")
                ]
            ),
            ToolDescriptor(
                name="set_recurring",
                description="Set up a recurring reminder",
                parameters=[
                    ToolParameter(name="title", type="string", required=True,
                                 description="Title of the recurring reminder"),
                    ToolParameter(name="message", type="string", required=True,
                                 description="Message for the reminder"),
                    ToolParameter(name="recurrence", type="string", required=True,
                                 description="daily, weekly, monthly, or yearly"),
                    ToolParameter(name="time", type="string", required=True,
                                 description="Time of day (HH:MM)")
                ]
            )
        ]
    
    def validate(self, invocation: ToolInvocation) -> bool:
        """Validate the invocation."""
        return invocation.tool_name in [t.name for t in self.discover_tools()]
    
    async def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        """Execute the reminder operation."""
        try:
            tool_name = invocation.tool_name
            params = invocation.parameters or {}
            
            if tool_name == "create_reminder":
                result = self._create_reminder(
                    title=params.get("title", ""),
                    message=params.get("message", ""),
                    scheduled_at=params.get("scheduled_at"),
                    priority=params.get("priority", "normal"),
                    recurrence=params.get("recurrence", "none")
                )
            elif tool_name == "list_reminders":
                result = self._list_reminders(params.get("status"))
            elif tool_name == "get_reminder":
                result = self._get_reminder(params.get("reminder_id", ""))
            elif tool_name == "snooze_reminder":
                result = self._snooze_reminder(
                    params.get("reminder_id", ""),
                    params.get("minutes", 5)
                )
            elif tool_name == "complete_reminder":
                result = self._complete_reminder(params.get("reminder_id", ""))
            elif tool_name == "cancel_reminder":
                result = self._cancel_reminder(params.get("reminder_id", ""))
            elif tool_name == "update_reminder":
                result = self._update_reminder(
                    params.get("reminder_id", ""),
                    params
                )
            elif tool_name == "set_recurring":
                result = self._set_recurring(
                    title=params.get("title", ""),
                    message=params.get("message", ""),
                    recurrence=params.get("recurrence", "daily"),
                    time=params.get("time", "09:00")
                )
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message=f"Unknown tool: {tool_name}"
                )
            
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                message="Operation completed",
                data=result
            )
            
        except Exception as e:
            logger.error(f"Reminder error: {e}")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=str(e)
            )
    
    def _create_reminder(
        self,
        title: str,
        message: str,
        scheduled_at: str,
        priority: str = "normal",
        recurrence: str = "none"
    ) -> Dict[str, Any]:
        """Create a new reminder."""
        reminder_id = str(uuid.uuid4())[:8]
        
        # Parse scheduled time
        try:
            scheduled_time = datetime.fromisoformat(scheduled_at)
        except ValueError:
            # Try parsing as timedelta from now
            if scheduled_at.startswith("+"):
                minutes = int(scheduled_at[1:])
                scheduled_time = datetime.now() + timedelta(minutes=minutes)
            else:
                raise ValueError(f"Invalid datetime format: {scheduled_at}")
        
        reminder = Reminder(
            id=reminder_id,
            title=title,
            message=message,
            priority=ReminderPriority(priority),
            status=ReminderStatus.PENDING,
            created_at=datetime.now(),
            scheduled_at=scheduled_time,
            recurrence=RecurrenceType(recurrence)
        )
        
        self._reminders[reminder_id] = reminder
        self._schedule_reminder(reminder)
        self._save()
        
        return {"created": True, "reminder": reminder.to_dict()}
    
    def _list_reminders(self, status: Optional[str] = None) -> Dict[str, Any]:
        """List all reminders."""
        reminders = list(self._reminders.values())
        
        if status:
            reminders = [r for r in reminders if r.status.value == status]
        
        # Sort by scheduled time
        reminders.sort(key=lambda r: r.scheduled_at)
        
        return {
            "reminders": [r.to_dict() for r in reminders],
            "total": len(reminders)
        }
    
    def _get_reminder(self, reminder_id: str) -> Dict[str, Any]:
        """Get a specific reminder."""
        reminder = self._reminders.get(reminder_id)
        if not reminder:
            return {"error": f"Reminder not found: {reminder_id}"}
        
        return {"reminder": reminder.to_dict()}
    
    def _snooze_reminder(self, reminder_id: str, minutes: int = 5) -> Dict[str, Any]:
        """Snooze a reminder."""
        reminder = self._reminders.get(reminder_id)
        if not reminder:
            return {"error": f"Reminder not found: {reminder_id}"}
        
        reminder.status = ReminderStatus.SNOOZED
        reminder.snoozed_until = datetime.now() + timedelta(minutes=minutes)
        reminder.snooze_count += 1
        
        # Cancel old timer and schedule new one
        self._cancel_timer(reminder_id)
        self._schedule_reminder(reminder)
        self._save()
        
        return {
            "snoozed": True,
            "reminder_id": reminder_id,
            "snoozed_until": reminder.snoozed_until.isoformat()
        }
    
    def _complete_reminder(self, reminder_id: str) -> Dict[str, Any]:
        """Mark a reminder as completed."""
        reminder = self._reminders.get(reminder_id)
        if not reminder:
            return {"error": f"Reminder not found: {reminder_id}"}
        
        reminder.status = ReminderStatus.COMPLETED
        self._cancel_timer(reminder_id)
        self._save()
        
        return {"completed": True, "reminder_id": reminder_id}
    
    def _cancel_reminder(self, reminder_id: str) -> Dict[str, Any]:
        """Cancel a reminder."""
        reminder = self._reminders.get(reminder_id)
        if not reminder:
            return {"error": f"Reminder not found: {reminder_id}"}
        
        reminder.status = ReminderStatus.CANCELLED
        self._cancel_timer(reminder_id)
        self._save()
        
        return {"cancelled": True, "reminder_id": reminder_id}
    
    def _update_reminder(self, reminder_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a reminder."""
        reminder = self._reminders.get(reminder_id)
        if not reminder:
            return {"error": f"Reminder not found: {reminder_id}"}
        
        if "title" in updates:
            reminder.title = updates["title"]
        if "message" in updates:
            reminder.message = updates["message"]
        if "scheduled_at" in updates:
            reminder.scheduled_at = datetime.fromisoformat(updates["scheduled_at"])
            # Reschedule
            self._cancel_timer(reminder_id)
            self._schedule_reminder(reminder)
        
        self._save()
        
        return {"updated": True, "reminder": reminder.to_dict()}
    
    def _set_recurring(
        self,
        title: str,
        message: str,
        recurrence: str,
        time: str
    ) -> Dict[str, Any]:
        """Set up a recurring reminder."""
        # Parse time
        hour, minute = map(int, time.split(":"))
        
        # Calculate next occurrence
        now = datetime.now()
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if next_run <= now:
            # Move to next period
            if recurrence == "daily":
                next_run += timedelta(days=1)
            elif recurrence == "weekly":
                next_run += timedelta(days=7)
            elif recurrence == "monthly":
                next_run = next_run.replace(month=next_run.month + 1 if next_run.month < 12 else 1)
            elif recurrence == "yearly":
                next_run = next_run.replace(year=next_run.year + 1)
        
        return self._create_reminder(
            title=title,
            message=message,
            scheduled_at=next_run.isoformat(),
            recurrence=recurrence
        )
    
    def _schedule_reminder(self, reminder: Reminder) -> None:
        """Schedule a reminder timer."""
        delay = (reminder.snoozed_until or reminder.scheduled_at) - datetime.now()
        
        if delay.total_seconds() <= 0:
            # Trigger immediately
            asyncio.create_task(self._trigger_reminder(reminder))
        else:
            # Schedule timer
            task = asyncio.create_task(self._delayed_trigger(reminder, delay.total_seconds()))
            self._active_timers[reminder.id] = task
    
    async def _delayed_trigger(self, reminder: Reminder, delay_seconds: float) -> None:
        """Wait and then trigger reminder."""
        try:
            await asyncio.sleep(delay_seconds)
            await self._trigger_reminder(reminder)
        except asyncio.CancelledError:
            pass
    
    async def _trigger_reminder(self, reminder: Reminder) -> None:
        """Trigger a reminder."""
        reminder.status = ReminderStatus.ACTIVE
        
        # Emit event
        if self._event_bus:
            self._event_bus.publish(ReminderTriggeredEvent(reminder))
        
        # Call notification callback
        if self._notification_callback:
            self._notification_callback(reminder)
        
        logger.info(f"Reminder triggered: {reminder.title}")
        
        # Handle recurrence
        if reminder.recurrence != RecurrenceType.NONE:
            self._schedule_next_recurrence(reminder)
        else:
            self._cancel_timer(reminder.id)
        
        self._save()
    
    def _schedule_next_recurrence(self, reminder: Reminder) -> None:
        """Schedule the next occurrence of a recurring reminder."""
        now = reminder.scheduled_at
        
        if reminder.recurrence == RecurrenceType.DAILY:
            next_run = now + timedelta(days=1)
        elif reminder.recurrence == RecurrenceType.WEEKLY:
            next_run = now + timedelta(weeks=1)
        elif reminder.recurrence == RecurrenceType.MONTHLY:
            month = now.month + 1 if now.month < 12 else 1
            year = now.year if now.month < 12 else now.year + 1
            next_run = now.replace(month=month, year=year)
        elif reminder.recurrence == RecurrenceType.YEARLY:
            next_run = now.replace(year=now.year + 1)
        else:
            return
        
        # Create new reminder instance
        new_reminder = Reminder(
            id=str(uuid.uuid4())[:8],
            title=reminder.title,
            message=reminder.message,
            priority=reminder.priority,
            status=ReminderStatus.PENDING,
            created_at=datetime.now(),
            scheduled_at=next_run,
            recurrence=reminder.recurrence,
            metadata=reminder.metadata
        )
        
        self._reminders[new_reminder.id] = new_reminder
        self._schedule_reminder(new_reminder)
    
    def _cancel_timer(self, reminder_id: str) -> None:
        """Cancel a reminder timer."""
        if reminder_id in self._active_timers:
            self._active_timers[reminder_id].cancel()
            del self._active_timers[reminder_id]
    
    def _start_monitor(self) -> None:
        """Start the reminder monitor."""
        self._monitor_task = asyncio.create_task(self._monitor_loop())
    
    async def _monitor_loop(self) -> None:
        """Monitor loop for checking reminders."""
        while self._state == ServiceState.RUNNING:
            try:
                now = datetime.now()
                
                for reminder in list(self._reminders.values()):
                    if reminder.status in [ReminderStatus.PENDING, ReminderStatus.SNOOZED]:
                        check_time = reminder.snoozed_until or reminder.scheduled_at
                        if now >= check_time:
                            await self._trigger_reminder(reminder)
                
                await asyncio.sleep(self._check_interval)
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(self._check_interval)
    
    def _stop_monitor(self) -> None:
        """Stop the reminder monitor."""
        if hasattr(self, '_monitor_task'):
            self._monitor_task.cancel()
    
    def _save(self) -> None:
        """Save reminders to disk."""
        os.makedirs(os.path.dirname(self._storage_path), exist_ok=True)
        
        data = {
            "reminders": [r.to_dict() for r in self._reminders.values()],
            "settings": self._storage.settings
        }
        
        with open(self._storage_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load(self) -> None:
        """Load reminders from disk."""
        if not os.path.exists(self._storage_path):
            return
        
        try:
            with open(self._storage_path, "r") as f:
                data = json.load(f)
            
            self._storage.reminders = data.get("reminders", [])
            self._storage.settings = data.get("settings", {})
            
            for reminder_data in self._storage.reminders:
                reminder = Reminder.from_dict(reminder_data)
                self._reminders[reminder.id] = reminder
                
                # Reschedule pending reminders
                if reminder.status in [ReminderStatus.PENDING, ReminderStatus.SNOOZED]:
                    self._schedule_reminder(reminder)
                    
        except Exception as e:
            logger.error(f"Failed to load reminders: {e}")
    
    def describe(self) -> CapabilityDescriptor:
        """Return capability descriptor."""
        return CapabilityDescriptor(
            id="reminder",
            version="1.0.0",
            name="Reminder System",
            description="Timed reminders, recurring alarms, and notifications",
            category="productivity",
            tags=["reminder", "alarm", "notification", "schedule"]
        )
