from desktop.models.environment import EnvironmentAction, EnvironmentContext, EnvironmentActionResult
from desktop.runtimes.environment.adapters.desktop.engine import IDesktopEngine

class Win32Engine(IDesktopEngine):
    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult:
        pass

class UIAutomationEngine(IDesktopEngine):
    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult:
        pass

class ShellEngine(IDesktopEngine):
    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult:
        pass

class PyAutoGUIEngine(IDesktopEngine):
    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult:
        pass

class OCRVisionEngine(IDesktopEngine):
    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult:
        pass
