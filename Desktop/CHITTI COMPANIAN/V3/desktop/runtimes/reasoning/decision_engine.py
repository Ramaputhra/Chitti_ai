import time
from typing import Dict, Any, List, Tuple
from desktop.models.reasoning import DecisionTrace
from desktop.models.retrieval import ContextPackage

class DecisionEngine:
    """
    Rule 297: Never retrieves directly. Only consumes ContextPackage.
    Combines policy intent, ContextPackage metadata, and Service Registry to make final decisions.
    """
    def __init__(self, service_registry=None):
        self.service_registry = service_registry

    def evaluate(self, intent: str, policy_results: Dict[str, bool], context: ContextPackage) -> Tuple[Dict[str, Any], List[DecisionTrace]]:
        """
        Takes the base policy results and refines them using the ContextPackage and ServiceRegistry.
        Returns the refined decisions and a list of DecisionTraces.
        """
        traces = []
        decisions = {
            "requires_retrieval": policy_results.get("retrieval", False),
            "requires_ai": policy_results.get("ai", False),
            "requires_presentation": policy_results.get("presentation", False),
            "requires_execution": policy_results.get("execution", False),
            "requires_confirmation": False,
            "requires_authentication": False,
            "preferred_services": []
        }
        
        # Trace Step 1: Base Policy
        traces.append(DecisionTrace(
            step="POLICY_EVALUATION",
            rule="Base rules from PolicyEngine",
            result=policy_results,
            confidence=1.0,
            timestamp=time.time()
        ))

        # Trace Step 2: Context Checking
        if decisions["requires_retrieval"] and context:
            if not context.knowledge_facts and not context.documents:
                # If we asked for retrieval but got nothing back, we might need AI to apologize or search web
                decisions["requires_ai"] = True
                traces.append(DecisionTrace(
                    step="CONTEXT_REFINEMENT",
                    rule="Empty context returned from retrieval",
                    result={"requires_ai": True},
                    confidence=0.9,
                    timestamp=time.time()
                ))

        # Trace Step 3: Capability Checking
        if decisions["requires_execution"] and self.service_registry:
            # Stub: check if capability exists
            # if not self.service_registry.has_service_for(intent):
            #    decisions["requires_execution"] = False
            #    decisions["requires_ai"] = True  # Fallback to AI
            pass
            
        # Example of a hardcoded safety rule
        if intent in ["DELETE_FILE", "SEND_EMAIL"]:
            decisions["requires_confirmation"] = True
            traces.append(DecisionTrace(
                step="SAFETY_CHECK",
                rule="Destructive intent detected",
                result={"requires_confirmation": True},
                confidence=1.0,
                timestamp=time.time()
            ))
            
        return decisions, traces
