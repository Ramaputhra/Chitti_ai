from abc import ABC, abstractmethod
from desktop.models.environment import EnvironmentAction, EnvironmentContext

class IDesktopEngine(ABC):
    """
    Rule 354: Hides native automation libraries like PyAutoGUI, Win32, or UIAutomation.
    """
    @abstractmethod
    def start(self): pass

    @abstractmethod
    def stop(self): pass

    @abstractmethod
    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> bool: pass

class PyAutoGUIEngine(IDesktopEngine):
    """
    PyAutoGUI / generic Win32 implementation stub.
    """
    def start(self):
        print("[PyAutoGUIEngine] Starting OS hook...")

    def stop(self):
        print("[PyAutoGUIEngine] Stopping OS hook...")

    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> bool:
        print(f"[PyAutoGUIEngine] Translating {action.action_type.name} to OS commands...")
        return True
