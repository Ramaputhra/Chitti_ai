from typing import Dict, Any
from desktop.models.presentation import CapabilityResult
from desktop.models.assessments import WorkflowAssessment, GoalAssessment, GoalStatus

class PresentationGenerator:
    """
    Consumes a CapabilityResult (which aggregates WorkflowAssessment and GoalAssessment) 
    and produces a structured representation suitable for rendering in the UI.
    """
    def generate(self, result: CapabilityResult) -> str:
        """Returns a string representation of the output (in the future, a JSON/HTML structured payload)."""
        if result.goal_assessment.status != GoalStatus.SATISFIED:
            return f"{result.capability_name} failed. Reason: {result.goal_assessment.evaluator_reasoning}"
            
        data = result.structured_data
        
        lines = [f"{result.capability_name} Successful", ""]
        total = 0
        
        # E.g. {"Documents": 2, "Images": 1}
        for category, count in data.items():
            lines.append(f"{category.ljust(15)} {count}")
            total += count
            
        lines.append("")
        lines.append(f"Total Files     {total}")
        lines.append("")
        lines.append(f"Completed in {result.metrics.duration_ms / 1000.0:.2f} sec")
        
        return "\n".join(lines)
