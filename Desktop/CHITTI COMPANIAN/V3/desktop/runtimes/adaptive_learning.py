import logging
import uuid
from datetime import datetime
from typing import Dict, Any

from desktop.models.alr_models import CapabilityCandidate, CapabilityVersion
from desktop.platform.ai.alr_services import (
    UnknownActionDetector, CapabilitySafetyEvaluator, WorkflowGeneralizer, 
    AutomaticReviewer, CapabilityPromoter
)
from desktop.platform.components.capability_registry import CapabilityRegistry

logger = logging.getLogger(__name__)

class AdaptiveLearningRuntime:
    """
    Orchestrates the Adaptive Capability Acquisition lifecycle.
    """
    def __init__(self, 
                 event_bus: Any,
                 planner: Any,
                 registry: CapabilityRegistry,
                 detector: UnknownActionDetector,
                 safety_evaluator: CapabilitySafetyEvaluator,
                 generalizer: WorkflowGeneralizer,
                 reviewer: AutomaticReviewer,
                 promoter: CapabilityPromoter):
        
        self.event_bus = event_bus
        self.planner = planner
        self.registry = registry
        self.detector = detector
        self.safety_evaluator = safety_evaluator
        self.generalizer = generalizer
        self.reviewer = reviewer
        self.promoter = promoter
        
        self._candidates: Dict[str, CapabilityCandidate] = {}

        # Subscribe to UNKNOWN_INTENT events
        self.event_bus.subscribe("UNKNOWN_INTENT", self.handle_unknown_intent)

    def handle_unknown_intent(self, event: Dict[str, Any]) -> None:
        intent_payload = event.get("payload", {})
        
        if not self.detector.is_action_request(intent_payload):
            logger.debug("Unknown intent is conversational. Ignored by ALR.")
            return
            
        logger.info(f"ALR intercepted actionable unknown intent: {intent_payload.get('name')}")
        
        # 1. Ask Planner for a workflow
        # workflow_plan = self.planner.plan(intent_payload)
        workflow_plan = {"primitives": ["SearchFile", "CopyFile"]} # Mock
        
        # 2. Safety Evaluation
        risk = self.safety_evaluator.evaluate_risk(workflow_plan)
        if risk.name == "RESTRICTED":
            logger.warning("ALR aborted: Workflow classified as RESTRICTED.")
            return
            
        # 3. Execute & Verify (Mocked here)
        success = True 
        
        if success:
            self._process_success(intent_payload.get("name", "UnknownAction"), workflow_plan, risk)

    def _process_success(self, name: str, workflow_plan: Dict[str, Any], risk: Any) -> None:
        if name not in self._candidates:
            # 4. Generalize
            generalized = self.generalizer.generalize(workflow_plan)
            
            candidate = CapabilityCandidate(
                candidate_id=str(uuid.uuid4()),
                name=name,
                workflow=generalized,
                risk_level=risk,
                version=CapabilityVersion(version_id=1),
                success_count=1
            )
            self._candidates[name] = candidate
            self.event_bus.publish("CAPABILITY_LEARNED", source="ALR", payload={"name": name, "risk": risk.name})
            logger.info(f"Learned new capability candidate: {name}")
        else:
            candidate = self._candidates[name]
            candidate.success_count += 1
            
            # 5. Review
            if self.reviewer.review(candidate):
                # 6. Promote
                decision = self.promoter.evaluate_for_promotion(candidate)
                if decision.promoted:
                    candidate.version.promoted_at = datetime.utcnow()
                    self.registry.register_learned(candidate.name, candidate.workflow)
                    self.event_bus.publish("CAPABILITY_PROMOTED", source="ALR", payload={"name": name, "version": 1})
                    logger.info(f"PROMOTED Candidate to Learned Registry: {name}")
