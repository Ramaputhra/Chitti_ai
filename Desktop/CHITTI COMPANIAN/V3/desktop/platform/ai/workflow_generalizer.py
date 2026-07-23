import logging
from typing import Dict, Any
from desktop.models.planner_models import ExecutionPlan

logger = logging.getLogger(__name__)

class WorkflowGeneralizer:
    """
    Strips explicit constants from a verified AI execution plan to create a reusable CapabilityCandidate.
    """
    def generalize(self, plan: ExecutionPlan) -> Dict[str, Any]:
        logger.info(f"WorkflowGeneralizer: Generalizing plan {plan.plan_id}")
        
        # In a physical implementation, this replaces literal string paths like "C:/Downloads" 
        # with parameters like "$target_dir" in the YAML graph.
        
        declarative_graph = {
            "version": "1.0",
            "type": "workflow_graph",
            "steps": []
        }
        
        for step in plan.steps:
            declarative_graph["steps"].append({
                "step_id": step.step_id,
                "capability_id": step.capability_id,
                # Generalization: Keep the keys, clear out the specific literal values for templating
                "parameters": {k: f"${k}" for k in step.parameters.keys()}
            })
            
        return declarative_graph
