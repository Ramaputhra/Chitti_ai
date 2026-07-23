import logging
import time
from typing import Any, Dict

from desktop.platform.core.response_builder import ResponseBuilder
from desktop.platform.core.persona_engine import PersonaEngine
from desktop.platform.core.presence_runtime import PresenceRuntime
from desktop.platform.components.adapters.expression_adapter import ExpressionAdapter
from desktop.models.presentation_models import (
    PresentationStartedEvent, PresentationCompletedEvent, FollowUpWindowOpenedEvent
)

logger = logging.getLogger(__name__)

class PresentationRuntime:
    """
    Rule 40: Presentation communicates verified truth.
    Subscribes to VERIFICATION_COMPLETED and WORKFLOW_FAILED.
    """
    def __init__(self, event_bus: Any, response_builder: ResponseBuilder, persona_engine: PersonaEngine, presence_runtime: PresenceRuntime, expression_adapter: ExpressionAdapter):
        self.event_bus = event_bus
        self.response_builder = response_builder
        self.persona_engine = persona_engine
        self.presence_runtime = presence_runtime
        self.expression_adapter = expression_adapter

    def handle_verification_completed(self, payload: Dict[str, Any]) -> None:
        event = payload.get("event")
        if not event: return
        
        logger.info("PresentationRuntime: Received verified execution. Building response.")
        
        # 1. Builder creates semantic intent
        response_intent = self.response_builder.build_response(
            workflow_id=event.context.workflow_id,
            capability_id=event.context.capability_id,
            status=event.status.name,
            parameters=event.context.parameters
        )
        
        # 2. Persona Engine applies personality and policies
        decision = self.persona_engine.generate_decision(response_intent)
        
        # 3. Publish Presentation Started
        start_ev = PresentationStartedEvent(workflow_id=event.context.workflow_id, decision=decision, timestamp=time.time())
        self.event_bus.publish("PRESENTATION_STARTED", source="PresentationRuntime", payload={"event": start_ev})
        
        # 4. Trigger physical presentation
        self.expression_adapter.present_decision(decision)
        
        # 5. Presence Engine manages the desktop lifecycle (e.g., Follow-Up Window)
        if decision.followup_window:
            logger.info("PresentationRuntime: Opening Follow-up Window")
            fu_ev = FollowUpWindowOpenedEvent(workflow_id=event.context.workflow_id, timestamp=time.time())
            self.event_bus.publish("FOLLOW_UP_WINDOW_OPENED", source="PresentationRuntime", payload={"event": fu_ev})
            self.presence_runtime.handle_workflow_completed()
            
        # 6. Publish Presentation Completed
        comp_ev = PresentationCompletedEvent(workflow_id=event.context.workflow_id, timestamp=time.time())
        self.event_bus.publish("PRESENTATION_COMPLETED", source="PresentationRuntime", payload={"event": comp_ev})
