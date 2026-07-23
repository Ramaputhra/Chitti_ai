import time
from typing import Any, Dict

from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.context import IContextEngine
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.state import IStateManager
from desktop.platform.shared.models.context import UnifiedContext, LanguageContext, RecentActivityBuffer, ActiveGoalContext


class ContextEngine(IContextEngine):
    def __init__(
        self,
        event_bus: IEventBus,
        logger: ILoggingService,
        state_manager: IStateManager,
    ) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self.state_manager = state_manager
        self._state = ServiceState.STOPPED

        self._current_task = None
        self._conversation_history = []
        self._language_context = LanguageContext()
        self._vision_context = {}
        self._desktop_context = {}
        self._world_state = None
        self._activity_buffer = RecentActivityBuffer()
        self._goal_context = ActiveGoalContext()

    @property
    def name(self) -> str:
        return "ContextEngine"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self.event_bus.subscribe(
            SystemEvents.LANGUAGE_TEXT_RECOGNIZED, self._on_text_recognized
        )
        self.event_bus.subscribe(
            SystemEvents.RESPONSE_GENERATED, self._on_response_generated
        )
        self.event_bus.subscribe(
            SystemEvents.ATTENTION_UPDATED, self._on_attention_updated
        )
        self.event_bus.subscribe(
            SystemEvents.WORLD_STATE_UPDATED, self._on_world_state_updated
        )
        self.event_bus.subscribe(
            SystemEvents.ACTIVITY_SESSION_ENDED, self._on_activity_session_ended
        )
        self.event_bus.subscribe(
            SystemEvents.ACTIVITY_SESSION_STARTED, self._on_activity_session_started
        )
        self.event_bus.subscribe(SystemEvents.PROJECT_ACTIVATED, self._on_project_activated)
        self.event_bus.subscribe(SystemEvents.GOAL_STARTED, self._on_goal_started)
        self.event_bus.subscribe(SystemEvents.GOAL_PROGRESS_UPDATED, self._on_goal_progress_updated)
        
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {"history_length": len(self._conversation_history)}

    def get_current_context(self) -> UnifiedContext:
        return UnifiedContext(
            timestamp=time.time(),
            system_state=self.state_manager.current_state.name,
            current_task=self._current_task,
            language_context=self._language_context,
            conversation_history=list(self._conversation_history),
            vision_context=dict(self._vision_context),
            desktop_context=dict(self._desktop_context),
            world_state=self._world_state,
            activity_buffer=self._activity_buffer,
            goal_context=self._goal_context,
        )

    def update_task(self, task_name: str) -> None:
        self._current_task = task_name
        self.logger.info(f"ContextEngine updated task: {task_name}")

    def _on_text_recognized(self, event: Event) -> None:
        text = event.payload.get("text", "")
        lang = event.payload.get("language", "en")
        
        # Update language context
        if lang in ["en", "te"]:
            self._language_context.spoken_language = lang
            self._language_context.preferred_response_language = lang
            if lang == "te":
                self._language_context.script = "Telugu"
                self._language_context.locale = "te-IN"
            else:
                self._language_context.script = "Latin"
                self._language_context.locale = "en-US"

        if text:
            self._conversation_history.append({"role": "user", "content": text})
            if len(self._conversation_history) > 10:
                self._conversation_history.pop(0)

    def _on_response_generated(self, event: Event) -> None:
        text = event.payload.get("text", "")
        if text:
            self._conversation_history.append({"role": "assistant", "content": text})
            if len(self._conversation_history) > 10:
                self._conversation_history.pop(0)

    def _on_attention_updated(self, event: Event) -> None:
        temporal_observations = event.payload.get("temporal_observations", [])
        updated = False
        
        vision_people = []
        
        for temp_obs in temporal_observations:
            obs = temp_obs.observation
            if obs.source == "vision":
                if obs.type == "person":
                    # Extract dict representation
                    person_data = obs.payload.__dict__.copy() if hasattr(obs.payload, "__dict__") else dict(obs.payload)
                    # Add temporal metadata
                    person_data["duration"] = temp_obs.duration
                    person_data["status"] = temp_obs.status.value
                    person_data["occurrence_count"] = temp_obs.occurrence_count
                    vision_people.append(person_data)
                    updated = True
            elif obs.source == "desktop":
                if obs.type == "active_app":
                    app_data = obs.payload.copy() if isinstance(obs.payload, dict) else dict(obs.payload)
                    app_data["duration"] = temp_obs.duration
                    app_data["status"] = temp_obs.status.value
                    self._desktop_context["active_app"] = app_data
                    updated = True
                    
        if vision_people or "people" in self._vision_context:
            self._vision_context["people"] = vision_people
            updated = True
            
        if updated:
            self.event_bus.publish(
                Event(
                    SystemEvents.CONTEXT_UPDATED,
                    self.name,
                    {"context": self.get_current_context()}
                )
            )

    def _on_world_state_updated(self, event: Event) -> None:
        world_state = event.payload.get("world_state")
        if world_state:
            self._world_state = world_state
            
            self.event_bus.publish(
                Event(
                    SystemEvents.CONTEXT_UPDATED,
                    self.name,
                    {"context": self.get_current_context()}
                )
            )

    def _on_activity_session_started(self, event: Event) -> None:
        session = event.payload.get("session")
        if session:
            self._activity_buffer.active_activity = session
            self.event_bus.publish(
                Event(
                    SystemEvents.CONTEXT_UPDATED,
                    self.name,
                    {"context": self.get_current_context()}
                )
            )

    def _on_activity_session_ended(self, event: Event) -> None:
        session = event.payload.get("session")
        if session:
            self._activity_buffer.previous_activity = self._activity_buffer.active_activity
            self._activity_buffer.active_activity = None
            
            self._activity_buffer.history.insert(0, session)
            if len(self._activity_buffer.history) > 5:
                self._activity_buffer.history.pop()
                
            self.event_bus.publish(
                Event(
                    SystemEvents.CONTEXT_UPDATED,
                    self.name,
                    {"context": self.get_current_context()}
                )
            )

    def _on_project_activated(self, event: Event) -> None:
        project = event.payload.get("project")
        if project:
            self._goal_context.current_project = project
            self.event_bus.publish(
                Event(
                    SystemEvents.CONTEXT_UPDATED,
                    self.name,
                    {"context": self.get_current_context()}
                )
            )

    def _on_goal_started(self, event: Event) -> None:
        goal = event.payload.get("goal")
        if goal:
            if self._goal_context.current_goal:
                self._goal_context.recent_goal = self._goal_context.current_goal
            self._goal_context.current_goal = goal
            self.event_bus.publish(
                Event(
                    SystemEvents.CONTEXT_UPDATED,
                    self.name,
                    {"context": self.get_current_context()}
                )
            )

    def _on_goal_progress_updated(self, event: Event) -> None:
        goal = event.payload.get("goal")
        if goal:
            # If a goal gets progress, it becomes the current active goal
            if self._goal_context.current_goal and self._goal_context.current_goal.goal_id != goal.goal_id:
                self._goal_context.recent_goal = self._goal_context.current_goal
            self._goal_context.current_goal = goal
            self.event_bus.publish(
                Event(
                    SystemEvents.CONTEXT_UPDATED,
                    self.name,
                    {"context": self.get_current_context()}
                )
            )
