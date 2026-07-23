from abc import ABC, abstractmethod
from desktop.models.environment import EnvironmentAction, EnvironmentContext, EnvironmentActionResult

class IIDEEngine(ABC):
    """
    Rule 357: Native IDE APIs, LSP implementations, or SDKs must never leak outside this boundary.
    """
    @abstractmethod
    def start(self): pass

    @abstractmethod
    def stop(self): pass

    @abstractmethod
    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult: pass

class VSCodeEngine(IIDEEngine):
    """
    VS Code API / extension stub.
    """
    def start(self):
        print("[VSCodeEngine] Establishing IPC with VS Code...")

    def stop(self):
        print("[VSCodeEngine] Disconnecting from VS Code...")

    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult:
        from desktop.models.environment import EnvironmentActionResult, ActionStatus
        
        print(f"[VSCodeEngine] Translating {action.action_type.name} to VS Code extension API...")
        return EnvironmentActionResult(
            status=ActionStatus.SUCCESS,
            latency=0.0
        )
