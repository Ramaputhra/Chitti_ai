import asyncio
from typing import Any, Callable, Optional
from desktop.ui.presence.presence_state import PresenceState, PresenceStateChanged
from desktop.ui.presence.animation_queue import AnimationQueue
from desktop.ui.presence.idle_manager import IdleManager

class PresenceEngine:
    """
    The single authority for everything the user visually perceives (Rule 3).
    Listens to the EventBus, updates State, and pushes to Animation Queue.
    """
    def __init__(self, event_bus: Any):
        self.event_bus = event_bus
        self.idle_manager = IdleManager(self._on_state_change)
        
        self._current_state = PresenceState.OFFLINE
        
        # Subscribe to Event Bus events
        if hasattr(self.event_bus, "subscribe"):
            self.event_bus.subscribe("WakeDetected", self._handle_wake)
            self.event_bus.subscribe("SpeechCaptured", self._handle_speech_captured)
            self.event_bus.subscribe("LLMStarted", self._handle_llm_started)
            self.event_bus.subscribe("AutomationStarted", self._handle_automation_started)
            self.event_bus.subscribe("TaskProgress", self._handle_task_progress)
            self.event_bus.subscribe("SPEECH_STATE_CHANGED", self._handle_speech_state)
            self.event_bus.subscribe("Voice.SpeakRequested", self._handle_speak_requested)
            self.event_bus.subscribe("Voice.SpeakCompleted", self._handle_speak_completed)
            self.event_bus.subscribe("Voice.SpeakInterrupted", self._handle_speak_interrupted)
            self.event_bus.subscribe("TaskCompleted", self._handle_task_completed)
            self.event_bus.subscribe("TaskFailed", self._handle_task_failed)
            self.event_bus.subscribe("ScheduledEventFired", self._handle_scheduled_event)
            self.event_bus.subscribe("FollowUpStarted", self._handle_follow_up)
            self.event_bus.subscribe("FollowUpEnded", self._handle_follow_up_ended)

    def start(self):
        # Initialize to SLEEPING or OFFLINE
        self._on_state_change(PresenceState.SLEEPING)

    def stop(self):
        pass

    def _on_state_change(self, state: PresenceState, context: Optional[Any] = None):
        """Processes an immediate state change and publishes the event."""
        self.idle_manager.on_state_changed(state)
        
        # Determine reason and metadata from context
        reason = None
        metadata = {}
        if context:
            if hasattr(context, "message"):
                reason = context.message
            elif isinstance(context, str):
                reason = context
            elif isinstance(context, dict):
                metadata = context
                
        # Rule 34 & 36: Publish the transition, do not invoke subscribers directly.
        if hasattr(self.event_bus, "publish"):
            event = PresenceStateChanged(
                previous=self._current_state,
                current=state,
                reason=reason,
                metadata=metadata
            )
            self.event_bus.publish(event)
            
        self._current_state = state
        
        # If we reach a terminal momentary state, automatically revert to READY
        if state in (PresenceState.SUCCESS, PresenceState.FAILURE, PresenceState.ERROR):
            import threading
            threading.Timer(0.1, self._revert_to_ready).start()

    def _revert_to_ready(self):
        self._on_state_change(PresenceState.READY)

    # --- Event Handlers ---
    def _handle_wake(self, event_data: Any):
        self._on_state_change(PresenceState.LISTENING)

    def _handle_speech_captured(self, event_data: Any):
        self._on_state_change(PresenceState.UNDERSTANDING)

    def _handle_speech_state(self, event_data: Any):
        payload = getattr(event_data, "payload", {})
        if isinstance(event_data, dict):
            payload = event_data.get("payload", {})
            
        state_str = payload.get("state")
        if state_str == "THINKING":
            self._on_state_change(PresenceState.THINKING)
        elif state_str == "UNDERSTANDING":
            self._on_state_change(PresenceState.UNDERSTANDING)
        elif state_str == "LISTENING":
            self._on_state_change(PresenceState.LISTENING)
        elif state_str == "SLEEPING":
            if self._current_state not in (PresenceState.TALKING, PresenceState.WORKING):
                self._on_state_change(PresenceState.SLEEPING)

    def _handle_llm_started(self, event_data: Any):
        self._on_state_change(PresenceState.THINKING)

    def _handle_automation_started(self, event_data: Any):
        is_background = getattr(event_data, "background", False)
        if hasattr(event_data, "get"):
            is_background = event_data.get("background", False)
            
        if is_background:
            self._on_state_change(PresenceState.MONITORING)
        else:
            self._on_state_change(PresenceState.WORKING)

    def _handle_task_progress(self, event_data: Any):
        self._on_state_change(PresenceState.WORKING, context=event_data)

    def _handle_speak_requested(self, event_data: Any):
        self._on_state_change(PresenceState.TALKING, context=event_data)

    def _handle_speak_completed(self, event_data: Any):
        if self._current_state == PresenceState.TALKING:
            self._on_state_change(PresenceState.READY)

    def _handle_speak_interrupted(self, event_data: Any):
        if self._current_state == PresenceState.TALKING:
            self._on_state_change(PresenceState.READY)

    def _handle_task_completed(self, event_data: Any):
        self._on_state_change(PresenceState.SUCCESS)

    def _handle_task_failed(self, event_data: Any):
        self._on_state_change(PresenceState.ERROR)
        
    def _handle_scheduled_event(self, event_data: Any):
        from desktop.ui.presence.presence_state import PresenceContext
        
        ctx = PresenceContext(
            task=getattr(event_data, "event", "Event"),
            message="Event Fired"
        )
        self._on_state_change(PresenceState.MONITORING, context=ctx)
        
    def _handle_follow_up(self, event_data: Any):
        self._on_state_change(PresenceState.WAITING)
        
    def _handle_follow_up_ended(self, event_data: Any):
        self._on_state_change(PresenceState.READY)
