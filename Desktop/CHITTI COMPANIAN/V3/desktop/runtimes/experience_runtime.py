import logging
import time
from typing import Dict, Any, List, Optional

from desktop.models.lifecycle import IRuntime, HealthState
from desktop.app.context import KernelContext
from desktop.models.experience import (
    ExperienceDefinition,
    ExperienceEligibilityRule,
    ExperienceSession,
    ExperienceHistoryRecord,
    ExperienceFeedback
)
from desktop.models.events import SystemEvent

logger = logging.getLogger(__name__)

class ExperienceRegistry:
    """
    Holds generic ExperienceDefinitions so the runtime can be completely generic.
    """
    def __init__(self):
        self._experiences: Dict[str, ExperienceDefinition] = {}

    def register(self, definition: ExperienceDefinition):
        self._experiences[definition.id] = definition
        logger.info(f"Registered Experience: {definition.name}")

    def get_by_trigger(self, trigger_name: str) -> List[ExperienceDefinition]:
        return [
            exp for exp in self._experiences.values()
            if trigger_name in exp.triggers
        ]

class ExperienceRuntime(IRuntime):
    """
    Sprint 7.1: Experience Runtime.
    Manages proactive companion experiences safely decoupled from deterministic capabilities.
    """
    def __init__(self):
        self.registry = ExperienceRegistry()
        self.context: Optional[KernelContext] = None
        self._history: List[ExperienceHistoryRecord] = []
        self._active_sessions: Dict[str, ExperienceSession] = {}
        self._running = False

    @property
    def dependencies(self) -> List[Any]:
        # Would typically depend on WorkflowRuntime, MemoryRuntime, PresenceRuntime
        return []

    async def initialize(self, context: KernelContext) -> bool:
        self.context = context
        # In a real scenario, this is where we'd subscribe to PresenceEvents and NotificationEvents
        return True

    async def start(self) -> bool:
        self._running = True
        logger.info("ExperienceRuntime started.")
        return True

    async def stop(self) -> bool:
        self._running = False
        return True

    def health(self) -> HealthState:
        return HealthState.HEALTHY

    async def shutdown(self) -> bool:
        return True

    # --- Core Pipeline ---

    async def handle_event(self, event: SystemEvent, event_data: dict):
        """
        Generic entrypoint. Checks if the incoming event triggers any experiences.
        """
        if not self._running:
            return

        trigger_name = event.event_type
        candidate_experiences = self.registry.get_by_trigger(trigger_name)
        
        # Sort by priority
        candidate_experiences.sort(key=lambda e: e.priority, reverse=True)

        for exp in candidate_experiences:
            score = self._evaluate_eligibility_score(exp, event_data)
            if score >= exp.minimum_score:
                await self._trigger_experience(exp, event_data, score)
                break # Only trigger highest priority eligible experience

    def _evaluate_eligibility_score(self, exp: ExperienceDefinition, event_data: dict) -> int:
        """
        Evaluates suppression, cooldown, and specific eligibility rules, returning a total score.
        """
        # 1. Cooldown check
        last_run = self._get_last_run_time(exp.id)
        if last_run and (time.time() - last_run) < exp.cooldown_seconds:
            logger.debug(f"Experience {exp.name} suppressed due to cooldown.")
            return 0

        # 2. Rule evaluation (Score Aggregation)
        total_score = 0
        for rule in exp.eligibility_rules:
            if self._evaluate_rule(rule, event_data):
                total_score += rule.score_contribution
                
        # 3. Apply penalties from feedback (Deterministic adaptation)
        penalty = self._calculate_feedback_penalty(exp.id)
        
        return max(0, total_score - penalty)

    def _calculate_feedback_penalty(self, experience_id: str) -> int:
        # Stub: If interrupted X times, subtract score
        return 0

    def _evaluate_rule(self, rule: ExperienceEligibilityRule, event_data: dict) -> bool:
        # Implementation of rule checking logic
        # e.g., if rule.rule_type == "presence_state": check if event_data matches
        # Placeholder for full generic rule evaluation
        return True

    async def _trigger_experience(self, exp: ExperienceDefinition, event_data: dict, score: int):
        """
        Builds the context and invokes the workflow for the experience.
        """
        logger.info(f"Triggering Experience: {exp.name} with score {score}")
        
        session = ExperienceSession(
            id=f"session_{int(time.time())}",
            experience_id=exp.id,
            context=event_data
        )
        self._active_sessions[session.id] = session
        
        # Log history
        record = ExperienceHistoryRecord(
            experience_id=exp.id,
            timestamp=time.time(),
            trigger=event_data.get("trigger", "unknown"),
            status="TRIGGERED",
            final_score=score
        )
        self._history.append(record)

        # Emit an event to Workflow Runtime
        # The Experience Runtime never speaks or executes directly (Rule 262).
        if self.context and hasattr(self.context, 'event_bus') and self.context.event_bus:
             # e.g. await self.context.event_bus.publish(...)
             pass

    def _get_last_run_time(self, experience_id: str) -> Optional[float]:
        # Search backwards in history
        for record in reversed(self._history):
            if record.experience_id == experience_id:
                return record.timestamp
        return None
