from abc import ABC, abstractmethod
from desktop.models.environment import EnvironmentAction, EnvironmentContext

class IBrowserEngine(ABC):
    """
    Rule 354: Native automation libraries are implementation details hidden behind this interface.
    """
    @abstractmethod
    def start(self): pass

    @abstractmethod
    def stop(self): pass

    @abstractmethod
    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> bool: pass

class PlaywrightEngine(IBrowserEngine):
    """
    Playwright implementation stub.
    """
    def start(self):
        print("[PlaywrightEngine] Starting Playwright instance...")

    def stop(self):
        print("[PlaywrightEngine] Stopping Playwright instance...")

    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> bool:
        print(f"[PlaywrightEngine] Executing {action.action_type.name}")
        return True
