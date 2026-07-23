import logging
from typing import Optional

from desktop.models.capability_models import CapabilityManifest
from desktop.models.planner_models import ExecutionGoal, WorkflowPlan, WorkflowStep, CapabilityResolution

logger = logging.getLogger(__name__)

class FastCapabilityResolverRuntime:
    """
    Optimizes simple commands to bypass the LLM Planner.
    If an ExecutionGoal maps directly to a single known capability (atomic action),
    it generates a single-step WorkflowPlan instantly.
    If the goal is complex or unknown, it returns None, deferring to the PlannerRuntime.
    """
    
    def resolve(self, goal: ExecutionGoal, available_manifests: list[CapabilityManifest]) -> Optional[WorkflowPlan]:
        # Fast resolution heuristic based on exact match of domain + action
        # E.g., domain="desktop", action="open" -> sys.file.open
        for manifest in available_manifests:
            # We map manifest ID segments to goal domain/action as a basic heuristic
            parts = manifest.id.split(".")
            if len(parts) >= 3 and parts[1] == goal.domain and parts[2] == goal.action:
                resolution = self._check_parameters(goal, manifest)
                if resolution:
                    logger.info(f"FastResolver hit for atomic capability: {manifest.id}")
                    step = WorkflowStep(
                        capability=resolution.capability,
                        parameters=resolution.parameters,
                        dependencies=[]
                    )
                    return WorkflowPlan(
                        goal_id=goal.session_id,
                        steps=[step]
                    )
                    
        # No fast atomic resolution found, route to PlannerRuntime
        logger.info(f"FastResolver missed. Goal requires PlannerRuntime.")
        return None
        
    def _check_parameters(self, goal: ExecutionGoal, manifest: CapabilityManifest) -> Optional[CapabilityResolution]:
        """
        Ensures all required parameters are available in the goal.
        """
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
