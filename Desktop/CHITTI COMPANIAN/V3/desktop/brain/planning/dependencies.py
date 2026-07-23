from desktop.brain.planning.models import ExecutionStep, InvalidPlanningStateException

class DependencyAnalyzer:
    def analyze_and_sequence(self, steps: list, budget: int) -> list:
        if budget <= 0:
            return []
            
        ordered = []
        visited = set()
        in_progress = set()
        
        step_map = {s.step_id: s for s in steps}
        
        def visit(step_id):
            if step_id in in_progress:
                raise InvalidPlanningStateException(f"Circular dependency detected at {step_id}")
            if step_id not in visited:
                in_progress.add(step_id)
                step = step_map.get(step_id)
                if step:
                    for dep in step.dependencies:
                        visit(dep)
                    ordered.append(step)
                in_progress.remove(step_id)
                visited.add(step_id)
                
        for s in steps:
            visit(s.step_id)
            
        return ordered
