from desktop.models.capability import CapabilityDescriptor, CapabilityParameter
from desktop.models.scheduling import ScheduledEvent, TriggerType, EventSource, EventOwner, EventPriority
import time

class TimeAssistantCapability:
    def __init__(self, time_runtime):
        self.time_runtime = time_runtime
        self.descriptor = CapabilityDescriptor(
            name="time_assistant",
            description="Manages Timers, Reminders, Alarms, Countdowns, and Timetable Plans. Implements the Temporal Rule.",
            parameters=[
                CapabilityParameter("action", "string", "The action to perform: schedule, cancel, list, snooze, next"),
                CapabilityParameter("duration", "integer", "Duration in seconds (for timers/snooze)", required=False),
                CapabilityParameter("label", "string", "The label or text for the reminder/timer", required=False),
                CapabilityParameter("event_id", "string", "The event ID to modify or cancel", required=False),
                CapabilityParameter("priority", "string", "Priority (CRITICAL, HIGH, NORMAL, LOW)", required=False)
            ]
        )
        
    async def invoke(self, params: dict):
        action = params.get("action")
        
        if action == "schedule":
            duration = params.get("duration", 0)
            label = params.get("label", "Timer")
            priority_str = params.get("priority", "NORMAL")
            
            trigger_time = time.time() + duration
            
            event = ScheduledEvent(
                trigger_type=TriggerType.TIME,
                trigger_time=trigger_time,
                label=label,
                payload_type="Timer" if duration < 3600 else "Reminder",
                priority=EventPriority[priority_str],
                source=EventSource.VOICE,
                owner=EventOwner.USER
            )
            
            await self.time_runtime.schedule(event)
            return {"status": "success", "event_id": event.id, "message": f"Scheduled '{label}' for {duration} seconds from now."}
            
        elif action == "snooze":
            event_id = params.get("event_id")
            duration = params.get("duration", 600) # Default 10 mins
            if not event_id:
                # If no specific event is given, find the most recently triggered one (mock logic for MVP)
                # In reality, conversation context would provide the event_id
                pass
            
            await self.time_runtime.extend(event_id, duration)
            return {"status": "success", "message": f"Snoozed event for {duration} seconds."}
            
        elif action == "next":
            evt = await self.time_runtime.next_event()
            if evt:
                return {"status": "success", "label": evt.label, "trigger_time": evt.trigger_time}
            return {"status": "empty", "message": "No upcoming events."}
            
        elif action == "list":
            events = await self.time_runtime.query()
            # Filter WAITING events
            active = [e for e in events if e.status.name == "WAITING"]
            return {"status": "success", "events": [{"id": e.id, "label": e.label} for e in active]}
            
        elif action == "cancel":
            event_id = params.get("event_id")
            await self.time_runtime.cancel(event_id)
            return {"status": "success"}

        return {"status": "error", "message": "Unknown action."}
