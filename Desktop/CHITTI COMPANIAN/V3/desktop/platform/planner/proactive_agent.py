import time
from typing import Optional, Dict
from desktop.app.context import KernelContext
from desktop.models.events import SystemEvent

class ProjectHistory:
    """
    Tracks user response history to proactive offers.
    Rule 37: Gradually personalize proactive behavior based on demonstrated user preferences.
    """
    def __init__(self):
        # project_name -> dict of stats
        self.history = {}
        
    def record_offer(self, project: str):
        if project not in self.history:
            self.history[project] = {"offers": 0, "accepted": 0, "declined": 0, "ignored": 0}
        self.history[project]["offers"] += 1
        
    def record_response(self, project: str, response: str):
        if project in self.history and response in ["accepted", "declined", "ignored"]:
            self.history[project][response] += 1
            
    def get_acceptance_rate(self, project: str) -> float:
        if project not in self.history or self.history[project]["offers"] == 0:
            return 0.0
        return self.history[project]["accepted"] / self.history[project]["offers"]

class ProactiveCooldown:
    """
    Prevents repeated annoying offers.
    Rule 36: Repeated declines should reduce proactive frequency through cooldowns.
    """
    def __init__(self):
        # project_name -> expiration_timestamp
        self._cooldowns: Dict[str, float] = {}
        
    def add_cooldown(self, project: str, duration_sec: float = 2 * 3600):
        self._cooldowns[project] = time.time() + duration_sec
        
    def is_cooling_down(self, project: str) -> bool:
        if project not in self._cooldowns:
            return False
        if time.time() > self._cooldowns[project]:
            del self._cooldowns[project]
            return False
        return True

class ProactiveAgent:
    """
    Planner extension that owns proactive behavior.
    Subscribes to SessionConfidenceChanged.
    """
    def __init__(self, context: KernelContext):
        self.context = context
        self.cooldown = ProactiveCooldown()
        self.project_history = ProjectHistory()
        # Track whether we've made an offer for this exact session
        self.offered_sessions: set = set()
        
    async def initialize(self):
        if self.context.event_bus:
            await self.context.event_bus.subscribe("SessionConfidenceChanged", self._on_confidence_changed)
            
    async def _on_confidence_changed(self, event: SystemEvent):
        data = event.data
        session_id = data.get("session_id")
        project = data.get("project")
        confidence = data.get("confidence", 0.0)
        
        # Rule 36: Requires Confidence
        if confidence < 0.90:
            return
            
        if session_id in self.offered_sessions:
            return
            
        if self.cooldown.is_cooling_down(project):
            return
            
        # We have high confidence. 
        # Retrieve previous WORK_SESSION from Memory
        # For MVP, we mock the Memory retrieval and previous session state
        previous_session = self._mock_retrieve_previous(project)
        if not previous_session:
            return
            
        # Compute Delta
        current_apps = {"VS Code", "Terminal"}  # Mocking current state
        delta_apps = previous_session["applications"] - current_apps
        
        if delta_apps:
            # Decide to help!
            self.offered_sessions.add(session_id)
            self.project_history.record_offer(project)
            
            acceptance_rate = self.project_history.get_acceptance_rate(project)
            await self._offer_assistance(project, delta_apps, acceptance_rate)
            
    def _mock_retrieve_previous(self, project: str) -> Optional[dict]:
        if project == "CHITTI_Companion":
            return {
                "applications": {"VS Code", "Terminal", "Chrome", "Explorer"}
            }
        return None
        
    async def _offer_assistance(self, project: str, delta: set, acceptance_rate: float):
        reason = f"Matched yesterday's work session for {project}. Missing {', '.join(delta)}."
        
        if acceptance_rate > 0.90:
            action = f"Restoring your usual {project} workspace."
            print(f"[ProactiveAgent - AUTO] {action} (Reason: {reason})")
            self.project_history.record_response(project, "accepted")
            # Execute AutomationPlan directly
        else:
            question = f"Looks like you're continuing your {project} work. Would you like me to restore the remaining workspace ({', '.join(delta)})?"
            print(f"[ProactiveAgent - ASK] {question} (Reason: {reason})")
            
            # Simulated response handling:
            # If accepted -> self.project_history.record_response(project, "accepted")
            # If declined -> self.project_history.record_response(project, "declined")
            #                self.cooldown.add_cooldown(project)
