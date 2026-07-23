from abc import ABC, abstractmethod
from typing import Any
from desktop.models.environment import EnvironmentAction, EnvironmentContext, EnvironmentActionResult

class IFileEngine(ABC):
    """
    Hides native OS filesystem calls. 
    Only the engine is aware of raw OS paths (e.g. C:\\Users\\...), preventing leakage.
    """
    @abstractmethod
    def start(self): pass

    @abstractmethod
    def stop(self): pass

    @abstractmethod
    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult: pass

class LocalFileEngine(IFileEngine):
    """
    Local filesystem implementation stub.
    """
    def start(self):
        print("[LocalFileEngine] Starting file engine...")

    def stop(self):
        print("[LocalFileEngine] Stopping file engine...")

    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult:
        from desktop.models.environment import EnvironmentActionResult, ActionStatus
        
        print(f"[LocalFileEngine] Translating {action.action_type.name} to OS filesystem commands...")
        # Simulate an immediate generic success result
        return EnvironmentActionResult(
            status=ActionStatus.SUCCESS,
            latency=0.0
        )
