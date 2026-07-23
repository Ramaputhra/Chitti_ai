import uuid
from desktop.brain.planning.models import ExecutionStep
from desktop.brain.planning.registry import CapabilityRegistry

class PlanCompiler:
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry
        
    def compile(self, intent: str, budget: int) -> list:
        if budget <= 0:
            return []
            
        template = self.registry.get_template(intent)
        if not template:
            return []
            
        steps = []
        for step_def in template.get("steps", []):
            steps.append(ExecutionStep(
                step_id=step_def.get("id", str(uuid.uuid4())),
                action_type=step_def.get("action_type", "UNKNOWN"),
                payload=step_def.get("payload", {}),
                dependencies=step_def.get("deps", [])
            ))
        return steps
