import random
import logging
from typing import Dict, Any

class ChaosMonkey:
    """
    Intentionally injects faults into the CHITTI runtime stack to validate 
    graceful degradation, fallbacks, and retry mechanisms.
    """
    def __init__(self, failure_probability: float = 0.0):
        self.failure_probability = failure_probability
        self.active_faults = set()
        
    def inject_fault(self, fault_name: str):
        print(f"[CHAOS] Injecting Fault: {fault_name}")
        self.active_faults.add(fault_name)
        
    def clear_faults(self):
        self.active_faults.clear()
        
    def check_fault(self, fault_name: str) -> bool:
        """Returns True if the fault is active, forcing the caller to degrade."""
        if fault_name in self.active_faults:
            return True
        if self.failure_probability > 0.0 and random.random() < self.failure_probability:
            print(f"[CHAOS] Random fault triggered: {fault_name}")
            return True
        return False

# Common Faults to Inject
FAULTS = {
    "WORLD_RUNTIME_UNAVAILABLE": "world_runtime_unavailable",
    "UIA_PROVIDER_CRASH": "uia_provider_crash",
    "GPU_OOM": "gpu_oom",
    "MODEL_LOAD_TIMEOUT": "model_load_timeout",
    "MEMORY_DB_LOCKED": "memory_db_locked"
}
