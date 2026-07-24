import logging
from typing import List, Optional, Tuple

from desktop.models.planner_models import ExecutionGoal, WorkflowPlan, WorkflowStep, CapabilityResolution
from desktop.models.capability_models import CapabilityManifest

logger = logging.getLogger(__name__)

# Alias for backward compatibility
CapabilityResolver = CapabilityResolverRuntime

class CapabilityResolverRuntime:
    """
    First-class runtime responsible for determining WHICH capability (or capabilities) can satisfy a goal.
    If it uniquely resolves to a single atomic capability, it instantly produces a WorkflowPlan (fast path).
    If there are multiple candidates, learned workflows, or no direct matches, it defers orchestration to the PlannerRuntime.
    """
    def __init__(self, registry: List[CapabilityManifest]):
        self._registry = registry

    def resolve(self, goal: ExecutionGoal) -> Tuple[Optional[WorkflowPlan], List[CapabilityResolution]]:
        logger.info(f"Resolving capabilities for ExecutionGoal: {goal.domain}.{goal.action}")
        
        candidates = []
        
        for manifest in self._registry:
            parts = manifest.id.split(".")
            if len(parts) >= 3 and parts[1] == goal.domain and parts[2] == goal.action:
                res = self._check_parameters(goal, manifest)
                if res:
                    candidates.append(res)
                    
        # Atomic Resolution: Exactly one candidate matches perfectly.
        if len(candidates) == 1:
            logger.info(f"CapabilityResolver hit fast path for atomic capability: {candidates[0].capability}")
            step = WorkflowStep(
                capability=candidates[0].capability,
                parameters=candidates[0].parameters,
                dependencies=[]
            )
            plan = WorkflowPlan(goal_id=goal.session_id, steps=[step])
            return plan, candidates
            
        # Multiple candidates or no direct match: Planner must orchestrate.
        logger.info(f"CapabilityResolver found {len(candidates)} candidates. Deferring to PlannerRuntime.")
        return None, candidates

    def _check_parameters(self, goal: ExecutionGoal, manifest: CapabilityManifest) -> Optional[CapabilityResolution]:
        resolved_params = {}
        for req_param in manifest.required_parameters:
            if req_param == "folder_path" and goal.target:
                resolved_params[req_param] = goal.target
            elif req_param in goal.parameters:
                resolved_params[req_param] = goal.parameters[req_param]
            else:
                return None
                
        return CapabilityResolution(
            capability=manifest.id,
            confidence=1.0,
            parameters=resolved_params
        )
