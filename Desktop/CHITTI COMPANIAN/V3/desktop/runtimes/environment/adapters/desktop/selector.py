from desktop.models.environment import EnvironmentAction, EnvironmentContext
from desktop.runtimes.environment.adapters.desktop.engine import IDesktopEngine
from desktop.runtimes.environment.adapters.desktop.engines.hybrid_engines import (
    Win32Engine, UIAutomationEngine, ShellEngine, PyAutoGUIEngine, OCRVisionEngine
)

class DesktopEngineSelector:
    """
    Routes EnvironmentActions to the most appropriate sub-engine.
    Does not implement IDesktopEngine itself.
    """
    def __init__(self):
        self.win32 = Win32Engine()
        self.uia = UIAutomationEngine()
        self.shell = ShellEngine()
        self.autogui = PyAutoGUIEngine()
        self.vision = OCRVisionEngine()
        
    def select_engine(self, action: EnvironmentAction, context: EnvironmentContext) -> IDesktopEngine:
        # Pseudo-routing logic based on action and health
        if action.action_type in ["OPEN_APPLICATION", "OPEN_RESOURCE"]:
            return self.shell
        elif action.action_type in ["FOCUS_WINDOW", "RESIZE_WINDOW"]:
            return self.win32
        elif action.action_type in ["CLICK", "SELECT"]:
            return self.uia
        
        # Fallback
        return self.autogui
