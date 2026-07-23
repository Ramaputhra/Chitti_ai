import uuid
from typing import List, Optional
from datetime import datetime
from desktop.models.observation import Observation
from desktop.models.activity import ActivitySession, ActivityEvent

class ActivityIntelligenceEngine:
    """
    Deterministically classifies objective Observation streams into ActivitySessions.
    Emits immutable ActivityEvents upon context switch.
    """
    def __init__(self):
        self.active_session: Optional[ActivitySession] = None
        self.emitted_events: List[ActivityEvent] = []

    def process_observation(self, obs: Observation):
        """Processes a new observation and updates or switches the active session."""
        activity_type, workspace_hint = self._classify_observation(obs)
        
        if not activity_type:
            # Unclassified observation, just append if it relates to current context? 
            # Or ignore. We will ignore for clean boundaries.
            return

        if self.active_session:
            if self.active_session.activity_type == activity_type and self.active_session.workspace_hint == workspace_hint:
                # Same context, update session
                self.active_session.last_update = obs.timestamp
                self.active_session.related_observations.append(obs.observation_id)
            else:
                # Context switch
                self._close_active_session(obs.timestamp)
                self._start_new_session(activity_type, workspace_hint, obs)
        else:
            self._start_new_session(activity_type, workspace_hint, obs)

    def _start_new_session(self, activity_type: str, workspace_hint: str, obs: Observation):
        self.active_session = ActivitySession(
            session_id=str(uuid.uuid4()),
            activity_type=activity_type,
            start_time=obs.timestamp,
            last_update=obs.timestamp,
            related_observations=[obs.observation_id],
            workspace_hint=workspace_hint
        )

    def _close_active_session(self, end_time: datetime):
        if not self.active_session:
            return
            
        # If closing purely due to end of tracking, we might use last_update. 
        # But if closing due to context switch, end_time is the new obs timestamp.
        self.active_session.end_time = end_time
        self.active_session.duration = (end_time - self.active_session.start_time).total_seconds()
        
        event = ActivityEvent(
            activity_id=self.active_session.session_id,
            activity_type=self.active_session.activity_type,
            start_time=self.active_session.start_time,
            end_time=self.active_session.end_time,
            duration=self.active_session.duration,
            related_observations=self.active_session.related_observations,
            workspace_hint=self.active_session.workspace_hint,
            confidence=self.active_session.confidence
        )
        self.emitted_events.append(event)
        self.active_session = None

    def _classify_observation(self, obs: Observation):
        """
        Deterministic Rule Engine matching observations to Activities.
        Returns Tuple(activity_type, workspace_hint)
        """
        if obs.observation_type == "window_state":
            title = obs.payload.get("title", "").lower()
            if "google docs" in title or "word" in title:
                return "Writing Activity", title
            if "youtube" in title:
                return "Video Watching Activity", title
            if "visual studio code" in title or "ide" in title:
                return "Coding Activity", title
            if "chrome" in title or "browser" in title:
                return "Web Research", title
                
        if obs.observation_type == "process_state":
            name = obs.payload.get("name", "").lower()
            if "git.exe" in name or "python.exe" in name or "msbuild.exe" in name:
                return "Build Activity", name
            if "code.exe" in name:
                return "Coding Activity", "Code.exe"
                
        if obs.observation_type == "filesystem_state":
            filepath = obs.payload.get("filepath", "").lower()
            if filepath.endswith(".py") or filepath.endswith(".js"):
                return "Coding Activity", filepath
                
        if obs.observation_type == "clipboard_state":
            # Very simplistic fallback: if they copy text, it might be research
            if obs.payload.get("type") == "text":
                return "Web Research", "Clipboard"
                
        return None, None
