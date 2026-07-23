from typing import Dict, Any

class ReasoningPolicyEngine:
    """
    Evaluates deterministic rules based on the intent string.
    Rule 296: Never executes capabilities.
    """
    def __init__(self):
        # Example policy table as requested
        self._policy_table = {
            "OPEN_APPLICATION": {"retrieval": False, "ai": False, "presentation": False, "execution": True},
            "CLOSE_APPLICATION": {"retrieval": False, "ai": False, "presentation": False, "execution": True},
            "SHOW_PRODUCTIVITY": {"retrieval": True, "ai": False, "presentation": True, "execution": False},
            "COMPARE_DOCUMENTS": {"retrieval": True, "ai": True, "presentation": True, "execution": False},
            "EXPLAIN_CONCEPT": {"retrieval": False, "ai": True, "presentation": False, "execution": False},
            "EXPORT_PRESENTATION": {"retrieval": False, "ai": False, "presentation": False, "execution": True},
            "EMAIL_REPORT": {"retrieval": False, "ai": False, "presentation": False, "execution": True},
        }
        
    def evaluate(self, intent: str) -> Dict[str, bool]:
        """
        Returns a dictionary of required capabilities based purely on intent.
        Fallback to safe defaults if intent is unknown.
        """
        if intent in self._policy_table:
            return self._policy_table[intent]
            
        # Default fallback: assume it needs LLM and Retrieval for safety
        return {"retrieval": True, "ai": True, "presentation": False, "execution": False}
