from desktop.capabilities.work_continuity.models import Recommendation, InterruptionPolicy, FocusState

class InterruptionPolicyEngine:
    """
    Evaluates recommendations against the user's current focus state to enforce Rule 138:
    "CHITTI must never interrupt focused work unless the expected value of the interruption
    exceeds the estimated disruption cost."
    """
    def evaluate(self, recommendation: Recommendation, current_focus: FocusState) -> Recommendation:
        # Default to PASSIVE (available but not actively interrupting)
        final_policy = InterruptionPolicy.PASSIVE
        
        # Calculate expected value
        expected_value = recommendation.estimated_value * recommendation.confidence
        
        # Calculate disruption cost based on focus state
        disruption_cost = self._estimate_disruption_cost(current_focus)
        
        # Rule 138 Logic
        if expected_value > disruption_cost:
            # The value is high enough to warrant a SUGGEST toast
            final_policy = InterruptionPolicy.SUGGEST
            
        # Exception: Critical data loss or emergencies always bypass the cost check
        if recommendation.priority >= 0.95:
            final_policy = InterruptionPolicy.URGENT
            
        # Exception: If the user is in deep flow, elevate the disruption cost artificially
        if current_focus == FocusState.FLOW and final_policy == InterruptionPolicy.SUGGEST:
            # Require an overwhelming value to break true flow state
            if expected_value < (disruption_cost * 2):
                final_policy = InterruptionPolicy.PASSIVE
                
        # Assign the calculated policy
        recommendation.policy = final_policy
        return recommendation

    def _estimate_disruption_cost(self, focus_state: FocusState) -> float:
        """Returns a scalar representing the cost of interrupting the user right now."""
        if focus_state == FocusState.FLOW:
            return 0.9  # Extremely high cost to interrupt
        elif focus_state == FocusState.RECOVERING:
            return 0.8  # They are trying to get back on track, don't break them
        elif focus_state == FocusState.NORMAL:
            return 0.4
        elif focus_state == FocusState.FRACTURED:
            return 0.1  # They are already distracted, low cost
        elif focus_state == FocusState.INTERRUPTED:
            return 0.05
        return 0.5
