from desktop.brain.execution.models import InvalidExecutionStateException

class ExecutionValidator:
    def validate_result(self, result, budget: int) -> bool:
        if budget <= 0:
            return False
            
        if not result.evidence_trace.execution_plan_id:
            raise InvalidExecutionStateException("Missing execution plan ID in trace")
            
        return True
