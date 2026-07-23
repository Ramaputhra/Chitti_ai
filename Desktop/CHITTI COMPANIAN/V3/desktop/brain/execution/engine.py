import uuid
import time
from desktop.brain.execution.models import (
    ExecutionResult, ExecutionStepResult, ExecutionTrace, ExecutionSession,
    ExecutionBudgetExceededException, InvalidExecutionStateException
)
from desktop.brain.execution.registry import CapabilityExecutionRegistry
from desktop.brain.execution.invoker import CapabilityInvoker
from desktop.brain.execution.monitor import ExecutionMonitor
from desktop.brain.execution.policies import RetryPolicy, RollbackPolicy
from desktop.brain.execution.validator import ExecutionValidator
from desktop.brain.execution.confidence import ExecutionConfidenceModel

class ExecutionEngine:
    def __init__(self):
        self.registry = CapabilityExecutionRegistry()
        
        self.registry.register_handler("OS_REGISTRY_EDIT", lambda p: ("SUCCESS", "edited", ""))
        self.registry.register_handler("RESTART_SERVICE", lambda p: ("SUCCESS", "restarted", ""))
        self.registry.register_handler("FAIL_ONCE", self._fail_once_handler)
        self.registry.register_handler("FAIL_ALWAYS", lambda p: ("FAILED", "", "fatal error"))
        
        self.invoker = CapabilityInvoker(self.registry)
        self.monitor = ExecutionMonitor()
        self.retry_policy = RetryPolicy(max_retries=3)
        self.rollback_policy = RollbackPolicy()
        self.validator = ExecutionValidator()
        self.confidence_model = ExecutionConfidenceModel()
        
        self._fail_once_state = 0
        
    def _fail_once_handler(self, payload):
        if self._fail_once_state == 0:
            self._fail_once_state = 1
            return ("FAILED", "", "temp error")
        return ("SUCCESS", "ok", "")
        
    def execute(self, execution_plan) -> ExecutionSession:
        max_duration = 30000
        max_monitor = 1000
        max_rollbacks = 10
        max_val = 1
        
        self.monitor.log_event("STATE", "CREATED", max_monitor)
        
        start_time = time.time()
        step_results = []
        overall_status = "COMPLETED"
        
        try:
            for step in execution_plan.steps:
                self.monitor.log_event("STATE", "DISPATCHING", max_monitor)
                self.monitor.log_event("STATE", "RUNNING", max_monitor)
                
                attempts = 0
                while True:
                    if (time.time() - start_time) * 1000 > max_duration:
                        raise ExecutionBudgetExceededException("Max duration exceeded")
                        
                    res = self.invoker.invoke(step, budget=1)
                    attempts += 1
                    
                    if res.status == "SUCCESS":
                        step_results.append(res)
                        break
                        
                    if not self.retry_policy.should_retry(attempts, res.status):
                        step_results.append(res)
                        overall_status = "FAILED"
                        break
                        
                if overall_status == "FAILED":
                    break
                    
            if overall_status == "FAILED":
                overall_status = self.rollback_policy.execute_rollback(step_results, max_rollbacks)
                
            self.monitor.log_event("STATE", "VALIDATING", max_monitor)
            
            trace = ExecutionTrace(
                execution_plan_id=getattr(execution_plan, "plan_id", "mock_pid"),
                compilation_trace=getattr(execution_plan, "evidence_trace", None)
            )
            
            final_conf = self.confidence_model.calculate(getattr(execution_plan, "plan_confidence", 1.0), step_results)
            
            result = ExecutionResult(
                result_id=str(uuid.uuid4()),
                overall_status=overall_status,
                step_results=step_results,
                execution_confidence=final_conf,
                evidence_trace=trace
            )
            
            self.validator.validate_result(result, max_val)
            max_val -= 1
            
            self.monitor.log_event("STATE", overall_status, max_monitor)
            
            return ExecutionSession(
                session_id=str(uuid.uuid4()),
                source_plan=execution_plan,
                monitor_logs=self.monitor.get_logs(),
                final_result=result
            )
            
        except ExecutionBudgetExceededException:
            result = ExecutionResult(
                result_id=str(uuid.uuid4()),
                overall_status="ABORTED",
                step_results=step_results,
                execution_confidence=0.0,
                evidence_trace=ExecutionTrace(getattr(execution_plan, "plan_id", "mock"), None)
            )
            return ExecutionSession(
                session_id=str(uuid.uuid4()),
                source_plan=execution_plan,
                monitor_logs=self.monitor.get_logs(),
                final_result=result
            )
