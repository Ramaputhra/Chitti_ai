import logging
from typing import Any, Dict

from desktop.platform.ai.workflow_generalizer import WorkflowGeneralizer
from desktop.platform.ai.capability_promoter import CapabilityPromoter
from desktop.platform.components.learned_capability_registry import LearnedCapabilityRegistry

logger = logging.getLogger(__name__)

class CapabilityAcquisitionRuntime:
    """
    Independent ACA Runtime orchestrator.
    Subscribes to VERIFICATION_COMPLETED. If the original intent was unknown,
    it triggers generalization and promotion.
    """
    def __init__(self, event_bus: Any, registry: LearnedCapabilityRegistry):
        self.event_bus = event_bus
        self.generalizer = WorkflowGeneralizer()
        self.promoter = CapabilityPromoter(registry)

    def handle_verification_completed(self, payload: Dict[str, Any]) -> None:
        event = payload.get("event")
        if not event: return
        
        # In a real environment, we check if this workflow originated from an "UNKNOWN" capability 
        # that had to be AI-planned dynamically.
        # For certification, we'll mock that check on the context.
        if event.context.parameters.get("was_unknown", False) and event.status.name == "SUCCESS":
            logger.info("ACA Runtime: Unknown workflow succeeded. Initiating learning loop.")
            
            # Retrieve the plan from the Kernel/Memory (mocked here as passed in params)
            plan = event.context.parameters.get("original_plan")
            if plan:
                # 1. Generalize
                declarative_graph = self.generalizer.generalize(plan)
                
                # 2. Promote
                intent_signature = event.context.parameters.get("intent_signature", "unknown_action")
                self.promoter.promote(intent_signature, declarative_graph)
