import time
from typing import Dict, Any

class RuntimeMetricsLogger:
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        
    def start_stage(self, stage_name: str, correlation_id: str):
        if correlation_id not in self.metrics:
            self.metrics[correlation_id] = {}
        self.metrics[correlation_id][stage_name] = {
            "start_timestamp": time.time(),
            "status": "RUNNING"
        }
        
    def end_stage(self, stage_name: str, correlation_id: str, status: str = "SUCCESS"):
        if correlation_id in self.metrics and stage_name in self.metrics[correlation_id]:
            stage_data = self.metrics[correlation_id][stage_name]
            stage_data["end_timestamp"] = time.time()
            stage_data["elapsed_time_ms"] = int((stage_data["end_timestamp"] - stage_data["start_timestamp"]) * 1000)
            stage_data["status"] = status
            
    def get_metrics(self, correlation_id: str) -> dict:
        return self.metrics.get(correlation_id, {})
