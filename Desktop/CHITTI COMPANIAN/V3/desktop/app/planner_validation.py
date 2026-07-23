from typing import Dict, Tuple, Optional
from desktop.models.cognition import CapabilityDescriptor, CapabilityRecommendation, PlanningDecision

class CapabilityValidator:
    """
    Deterministically validates LLM recommendations against registered CapabilityDescriptors.
    Rule 196: Capability Recommendations Are Advisory
    """
    def __init__(self, registry: Dict[str, CapabilityDescriptor]):
        self.registry = registry
        
    def validate(self, recommendation: CapabilityRecommendation) -> Tuple[Optional[PlanningDecision], list[str]]:
        """
        Returns (PlanningDecision, missing_parameters)
        """
        if not recommendation.candidate_capabilities:
            return None, []
            
        # We'll take the highest confidence valid capability
        sorted_caps = sorted(recommendation.candidate_capabilities, key=lambda x: x.confidence, reverse=True)
        
        for cap in sorted_caps:
            descriptor = self.registry.get(cap.capability_name)
            if not descriptor:
                continue # Reject hallucinated capability
                
            # Validate schema and find missing
            missing = []
            valid_params = {}
            for param in descriptor.parameter_schema:
                param_name = param["name"]
                is_required = param.get("required", False)
                
                if param_name in cap.parameters:
                    # In a real system, we'd also check the type here (string vs datetime etc)
                    valid_params[param_name] = cap.parameters[param_name]
                elif is_required:
                    missing.append(param_name)
                    
            if missing:
                # If required parameters are missing, we still return the decision structure
                # but the caller should route to Clarification
                return PlanningDecision(
                    workflow_name="ClarificationWorkflow",
                    confidence=cap.confidence,
                    parameters={"missing_parameters": missing, "intent": cap.capability_name},
                    requires_approval=False
                ), missing
                
            return PlanningDecision(
                workflow_name=cap.capability_name,
                confidence=cap.confidence,
                parameters=valid_params,
                requires_approval=False # Derived from policy in reality
            ), []
            
        return None, []
