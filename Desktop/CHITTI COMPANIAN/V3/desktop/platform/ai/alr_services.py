import logging
from typing import Any, Dict
from desktop.models.alr_models import CapabilityRisk, CapabilityCandidate, PromotionDecision, GeneralizedWorkflow

logger = logging.getLogger(__name__)

class UnknownActionDetector:
    def is_action_request(self, semantic_intent: Dict[str, Any]) -> bool:
        """
        Determines if the unknown intent is actionable (e.g., Compress, Merge) 
        rather than conversational (e.g., Explain, Tell me).
        """
        # Mock logic
        action_verbs = ["organize", "convert", "rename", "compress", "merge", "extract", "delete", "format"]
        intent_name = semantic_intent.get("name", "").lower()
        return any(verb in intent_name for verb in action_verbs)

class CapabilitySafetyEvaluator:
    def evaluate_risk(self, workflow_plan: Dict[str, Any]) -> CapabilityRisk:
        """
        Classifies risk based on primitives.
        """
        primitives = workflow_plan.get("primitives", [])
        if "FormatDrive" in primitives or "EditRegistry" in primitives:
            return CapabilityRisk.RESTRICTED
        if "DeleteFile" in primitives or "Shutdown" in primitives:
            return CapabilityRisk.PRIVILEGED
        if "RenameFile" in primitives or "MoveFile" in primitives:
            return CapabilityRisk.CAUTION
        return CapabilityRisk.SAFE

class WorkflowGeneralizer:
    def generalize(self, raw_execution_graph: Dict[str, Any]) -> GeneralizedWorkflow:
        """
        Strips hardcoded paths and inserts parameter variables.
        """
        # Mock implementation returning a dummy GeneralizedWorkflow
        return GeneralizedWorkflow(nodes=[], edges=[], parameters={})

class AutomaticReviewer:
    def review(self, candidate: CapabilityCandidate) -> bool:
        """
        Checks for infinite loops, missing params, and primitive adherence.
        """
        if candidate.risk_level == CapabilityRisk.RESTRICTED:
            logger.warning(f"Rejecting {candidate.name}: RESTRICTED risk level.")
            return False
            
        # Add checks for python generation, recursion, etc.
        return True

class CapabilityPromoter:
    def evaluate_for_promotion(self, candidate: CapabilityCandidate) -> PromotionDecision:
        """
        Determines if the candidate is ready for the registry.
        """
        if candidate.success_count >= 3:
            if candidate.risk_level in [CapabilityRisk.PRIVILEGED]:
                return PromotionDecision(promoted=False, reason="Privileged capabilities require explicit human approval.", requires_human=True)
            return PromotionDecision(promoted=True, reason="Success threshold met.", requires_human=False)
        
        return PromotionDecision(promoted=False, reason="Insufficient success count.", requires_human=False)
