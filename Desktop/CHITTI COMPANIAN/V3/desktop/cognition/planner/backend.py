from abc import ABC, abstractmethod
import time
import uuid
from desktop.models.cognition import ReasoningContext, Goal, GoalState
from desktop.models.intent import IntentType
from desktop.cognition.planner.continuity import ContinuityAssessor

class PlannerBackend(ABC):
    @abstractmethod
    def select_goal(self, context: ReasoningContext) -> Goal:
        pass

class DeterministicBackend(PlannerBackend):
    """
    Rule 55: Planner Authority. 
    Temporary deterministic fallback to select a goal until a semantic LLM backend is integrated.
    Incorporates Rule 56: Goal Continuity via ContinuityAssessor.
    """
    def select_goal(self, context: ReasoningContext) -> Goal:
        candidates = context.intent_candidates
        
        # 1. Assess Continuity
        continuity = ContinuityAssessor.assess(context)
        
        # Find the target recent goal if there is one
        recent_goal = None
        if continuity.target_goal_id:
            recent_goal = next((g for g in context.recent_goals if g.goal_id == continuity.target_goal_id), None)
            
        now = time.time()
        
        # 2. Handle continuity states
        if continuity.status == "CONTINUATION" and recent_goal:
            # We are continuing the previous goal
            new_state = GoalState(
                goal_id=recent_goal.goal_id,
                status="CONTINUED",
                timestamp=now,
                decision_basis=continuity.reasoning
            )
            recent_goal.state_history.append(new_state)
            return recent_goal
            
        elif continuity.status == "COMPLETION" and recent_goal:
            # The previous goal is complete. We mark it complete.
            # In a real system, we'd emit an event and establish a new goal.
            # For this mock, we just return the completed goal to be saved, 
            # and potentially a new goal. We'll just return the completed one to show the state change.
            new_state = GoalState(
                goal_id=recent_goal.goal_id,
                status="COMPLETED",
                timestamp=now,
                decision_basis=continuity.reasoning
            )
            recent_goal.state_history.append(new_state)
            return recent_goal
            
        elif continuity.status == "PAUSED" and recent_goal:
            # The previous goal is paused. We'd mark it paused, and create a new goal.
            new_state = GoalState(
                goal_id=recent_goal.goal_id,
                status="PAUSED",
                timestamp=now,
                decision_basis=continuity.reasoning
            )
            recent_goal.state_history.append(new_state)
            # Flow through to create the NEW goal
            pass

        # 3. Establish NEW goal
        if not candidates:
            # Fallback if no intents at all
            new_goal_id = str(uuid.uuid4())
            new_goal = Goal(
                goal_id=new_goal_id,
                intent_type=IntentType.EXPLORE_CODEBASE,
                created_at=now,
                state_history=[]
            )
            new_goal.state_history.append(GoalState(
                goal_id=new_goal_id,
                status="ACTIVE",
                timestamp=now,
                decision_basis=["No Intent Candidates Provided"]
            ))
            return new_goal
            
        # Select highest strength candidate deterministically
        strength_rank = {"DETERMINISTIC": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        selected = max(candidates, key=lambda c: strength_rank.get(c.strength.value, 0))
        
        new_goal_id = str(uuid.uuid4())
        new_goal = Goal(
            goal_id=new_goal_id,
            intent_type=selected.intent_type,
            created_at=now,
            state_history=[]
        )
        new_goal.state_history.append(GoalState(
            goal_id=new_goal_id,
            status="ACTIVE",
            timestamp=now,
            decision_basis=["Selected highest strength Intent Candidate"] + continuity.reasoning
        ))
        
        return new_goal
