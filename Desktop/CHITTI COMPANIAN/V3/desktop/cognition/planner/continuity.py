from desktop.models.cognition import ReasoningContext, ContinuityAssessment

class ContinuityAssessor:
    """
    Rule 56: Goal Continuity.
    Evaluates observable continuity between the current reasoning context 
    and previously established goals. 
    Outputs a ContinuityAssessment (CONTINUATION, COMPLETION, PAUSED, NEW).
    """
    @staticmethod
    def assess(context: ReasoningContext) -> ContinuityAssessment:
        if not context.recent_goals:
            return ContinuityAssessment(
                status="NEW",
                reasoning=["No recent goals found for this project."]
            )
            
        # For this deterministic placeholder, we just look at the most recent goal
        # and the strongest intent candidate.
        recent_goal = context.recent_goals[-1]
        
        if not context.intent_candidates:
            return ContinuityAssessment(
                status="PAUSED",
                target_goal_id=recent_goal.goal_id,
                reasoning=["No current intents detected. Assuming previous goal is paused."]
            )
            
        strongest_candidate = max(
            context.intent_candidates, 
            key=lambda c: {"DETERMINISTIC": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(c.strength.value, 0)
        )
        
        # Rule: Exact intent match -> CONTINUATION
        if strongest_candidate.intent_type == recent_goal.intent_type:
            return ContinuityAssessment(
                status="CONTINUATION",
                target_goal_id=recent_goal.goal_id,
                reasoning=[f"Current intent ({strongest_candidate.intent_type.value}) matches previous goal."]
            )
            
        # Rule: Category match (e.g. DEBUGGING -> VALIDATION might be continuation, but for 
        # this simple deterministic backend, we'll say if it's in the same category it's a continuation)
        # Actually, let's say if we see VALIDATE_CHANGES after FIX_BUILD, it's COMPLETION of FIX_BUILD.
        if recent_goal.intent_type.value == "FIX_BUILD" and strongest_candidate.intent_type.value == "VALIDATE_CHANGES":
            return ContinuityAssessment(
                status="COMPLETION",
                target_goal_id=recent_goal.goal_id,
                reasoning=["Validation intent follows a fix intent. Suggests completion of the fix."]
            )
            
        # Otherwise, assume PAUSED (conservative ABANDONED)
        return ContinuityAssessment(
            status="PAUSED",
            target_goal_id=recent_goal.goal_id,
            reasoning=[f"Current intent ({strongest_candidate.intent_type.value}) differs from previous goal. Pausing previous."]
        )
