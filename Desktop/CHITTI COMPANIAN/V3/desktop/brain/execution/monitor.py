class ExecutionMonitor:
    def __init__(self):
        self.logs = []
        
    def log_event(self, event_type: str, message: str, budget: int):
        if len(self.logs) >= budget:
            return
        self.logs.append({"type": event_type, "msg": message})
        
    def get_logs(self) -> dict:
        return {"events": self.logs}
