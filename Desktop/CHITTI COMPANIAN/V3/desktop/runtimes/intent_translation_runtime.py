import logging
from typing import Optional
from desktop.models.semantic_models import DesktopIntent
from desktop.models.planner_models import ExecutionGoal

logger = logging.getLogger(__name__)

class IntentTranslationRuntime:
    """
    Translates semantic meaning (DesktopIntent) into execution semantics (ExecutionGoal).
    This strictly decouples language understanding from execution planning.
    """
    
    def translate(self, intent: DesktopIntent) -> Optional[ExecutionGoal]:
        logger.info(f"Translating DesktopIntent to ExecutionGoal: {intent.type} -> {intent.action}")
        
        # Simple heuristic mapping for MVP / Experience 001.
        # Future implementations would use an ALR or semantic mapper here.
        domain = "desktop"
        action = intent.action.lower() if intent.action else "unknown"
        target = intent.target if intent.target else ""
        
        # Map parameters directly
        params = intent.parameters.copy() if intent.parameters else {}
        
        goal = ExecutionGoal(
            domain=domain,
            action=action,
            target=target,
            parameters=params,
            session_id=intent.session_id
        )
        
        logger.info(f"Translated to ExecutionGoal: domain={domain}, action={action}, target={target}")
        return goal
