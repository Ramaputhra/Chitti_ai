class RetryPolicy:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        
    def should_retry(self, attempt_count: int, status: str) -> bool:
        return status == "FAILED" and attempt_count < self.max_retries

class RollbackPolicy:
    def __init__(self):
        self.rollbacks_executed = 0
        
    def execute_rollback(self, step_results: list, budget: int) -> str:
        if self.rollbacks_executed >= budget:
            return "FAILED"
        self.rollbacks_executed += 1
        return "ROLLED_BACK"
