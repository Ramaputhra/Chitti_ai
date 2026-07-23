import asyncio
import sqlite3
import json
import time
from typing import List, Optional, Any, Dict
from dataclasses import asdict

from desktop.models.lifecycle import IRuntime, HealthState
from desktop.models.scheduling import (
    ScheduledEvent, EventStatus, TriggerType, EventSource, EventOwner, 
    EventCondition, RetryPolicy, EventResolution, EventPriority, EventRecurrence
)
from desktop.app.context import KernelContext
from desktop.models.events import SystemEvent

class ScheduledEventFired(SystemEvent):
    def __init__(self, event: ScheduledEvent):
        super().__init__("ScheduledEventFired", {"event_id": event.id, "label": event.label})
        self.event = event

class ActivityTimelineEvent(SystemEvent):
    def __init__(self, event_id: str, transition: str, label: str):
        super().__init__("ActivityTimelineEvent", {
            "event_id": event_id,
            "transition": transition,
            "label": label,
            "timestamp": time.time()
        })

class TimeRuntime(IRuntime):
    """
    Temporal Intelligence Layer. (Rule 6: Time Rule).
    Owns all waiting mechanisms (Timers, Reminders, Conditions, Timetables).
    """
    def __init__(self, db_path: str = "chitti_time.db"):
        self.db_path = db_path
        self._running = False
        self.context: Optional[KernelContext] = None
        self._task: Optional[asyncio.Task] = None
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_events (
                    id TEXT PRIMARY KEY,
                    trigger_type TEXT,
                    trigger_time REAL,
                    condition TEXT,
                    label TEXT,
                    payload_type TEXT,
                    payload_data TEXT,
                    status TEXT,
                    priority TEXT,
                    recurrence TEXT,
                    source TEXT,
                    owner TEXT,
                    retry_policy TEXT,
                    resolution TEXT,
                    created_at REAL,
                    updated_at REAL,
                    completed_at REAL
                )
            ''')

    @property
    def dependencies(self):
        return []

    def health(self) -> HealthState:
        return HealthState.HEALTHY
            
    async def initialize(self, context: KernelContext) -> bool:
        self.context = context
        self._init_db()
        # On initialization, mark all PENDING/WAITING events as Recovered if from previous boot?
        # User requested: Reboot PC -> Reminder restored.
        return True
        
    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._loop())
        
    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            
    async def shutdown(self):
        pass
        
    def _row_to_event(self, row) -> ScheduledEvent:
        return ScheduledEvent(
            id=row[0],
            trigger_type=TriggerType(row[1]),
            trigger_time=row[2],
            condition=EventCondition(row[3]) if row[3] else None,
            label=row[4],
            payload_type=row[5],
            payload_data=json.loads(row[6]) if row[6] else {},
            status=EventStatus(row[7]),
            priority=EventPriority[row[8]],
            recurrence=EventRecurrence(row[9]),
            source=EventSource(row[10]),
            owner=EventOwner(row[11]),
            retry_policy=RetryPolicy(row[12]),
            resolution=EventResolution(row[13]) if row[13] else None,
            created_at=row[14],
            updated_at=row[15],
            completed_at=row[16]
        )

    def _save_event(self, event: ScheduledEvent):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO scheduled_events 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.id, event.trigger_type.value, event.trigger_time,
                event.condition.value if event.condition else None,
                event.label, event.payload_type, json.dumps(event.payload_data),
                event.status.value, event.priority.name, event.recurrence.value,
                event.source.value, event.owner.value, event.retry_policy.value,
                event.resolution.value if event.resolution else None,
                event.created_at, event.updated_at, event.completed_at
            ))

    async def schedule(self, event: ScheduledEvent):
        event.status = EventStatus.SCHEDULED
        self._save_event(event)
        await self.context.event_bus.publish("ActivityTimelineEvent", ActivityTimelineEvent(event.id, "CREATED -> SCHEDULED", event.label))
        
        event.status = EventStatus.WAITING
        self._save_event(event)
        await self.context.event_bus.publish("ActivityTimelineEvent", ActivityTimelineEvent(event.id, "SCHEDULED -> WAITING", event.label))
        
    async def extend(self, event_id: str, additional_seconds: float):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM scheduled_events WHERE id = ?", (event_id,))
            row = cursor.fetchone()
            if row:
                event = self._row_to_event(row)
                if event.trigger_time:
                    event.trigger_time += additional_seconds
                    event.status = EventStatus.WAITING
                    event.updated_at = time.time()
                    self._save_event(event)
                    await self.context.event_bus.publish("ActivityTimelineEvent", ActivityTimelineEvent(event.id, "SNOOZED / EXTENDED", event.label))
    
    async def cancel(self, event_id: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM scheduled_events WHERE id = ?", (event_id,))
            row = cursor.fetchone()
            if row:
                event = self._row_to_event(row)
                event.status = EventStatus.CANCELLED
                self._save_event(event)
                
    async def query(self, status: EventStatus = None) -> List[ScheduledEvent]:
        events = []
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM scheduled_events"
            params = ()
            if status:
                query += " WHERE status = ?"
                params = (status.value,)
            for row in conn.execute(query, params):
                events.append(self._row_to_event(row))
        return events
        
    async def next_event(self) -> Optional[ScheduledEvent]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM scheduled_events 
                WHERE status = 'WAITING' AND trigger_type = 'TIME'
                ORDER BY trigger_time ASC LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                return self._row_to_event(row)
        return None

    async def wait_for(self, condition: EventCondition, **kwargs) -> ScheduledEvent:
        """
        Rule 6 (Temporal Rule): Planners block on this rather than writing custom wait loops.
        """
        event = ScheduledEvent(
            trigger_type=TriggerType.CONDITION,
            condition=condition,
            label=kwargs.get("label", f"Waiting for {condition.value}"),
            payload_data=kwargs,
            status=EventStatus.WAITING,
            source=EventSource.SYSTEM,
            owner=EventOwner.SYSTEM
        )
        await self.schedule(event)
        
        # In a real async environment we would return an asyncio.Future or await an Event.
        # For this MVP stub, we just return the event object to indicate it was scheduled.
        return event

    async def _loop(self):
        """Background polling loop for time-based triggers."""
        while self._running:
            now = time.time()
            triggered = []
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM scheduled_events 
                    WHERE status = 'WAITING' AND trigger_type = 'TIME' AND trigger_time <= ?
                """, (now,))
                
                for row in cursor.fetchall():
                    event = self._row_to_event(row)
                    event.status = EventStatus.TRIGGERED
                    event.updated_at = now
                    self._save_event(event)
                    triggered.append(event)
                    
            for event in triggered:
                await self.context.event_bus.publish("ActivityTimelineEvent", ActivityTimelineEvent(event.id, "WAITING -> TRIGGERED", event.label))
                # Publish the main event
                await self.context.event_bus.publish("ScheduledEventFired", ScheduledEventFired(event))
                
                # Transition to Follow Up mode logically
                event.status = EventStatus.FOLLOW_UP
                self._save_event(event)
                
            await asyncio.sleep(0.5)
