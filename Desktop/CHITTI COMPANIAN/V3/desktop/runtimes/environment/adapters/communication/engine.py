from abc import ABC, abstractmethod
from desktop.models.environment import EnvironmentAction, EnvironmentContext, EnvironmentActionResult, ActionStatus

class ICommunicationEngine(ABC):
    @abstractmethod
    def start(self): pass
    @abstractmethod
    def stop(self): pass

# --- Email Engines ---
class IEmailEngine(ICommunicationEngine):
    @abstractmethod
    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult: pass

class SMTPEngine(IEmailEngine):
    def start(self): print("[SMTPEngine] Connecting to SMTP/IMAP servers...")
    def stop(self): print("[SMTPEngine] Disconnecting...")
    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult:
        print(f"[SMTPEngine] Executing {action.action_type.name}")
        return EnvironmentActionResult(status=ActionStatus.SUCCESS, latency=0.0)

# --- Calendar Engines ---
class ICalendarEngine(ICommunicationEngine):
    @abstractmethod
    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult: pass

class GoogleCalendarEngine(ICalendarEngine):
    def start(self): print("[GoogleCalendarEngine] Initializing Google API client...")
    def stop(self): print("[GoogleCalendarEngine] Disposing client...")
    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult:
        print(f"[GoogleCalendarEngine] Executing {action.action_type.name}")
        return EnvironmentActionResult(status=ActionStatus.SUCCESS, latency=0.0)

# --- API Engines ---
class IAPIEngine(ICommunicationEngine):
    @abstractmethod
    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult: pass

class RESTEngine(IAPIEngine):
    def start(self): print("[RESTEngine] Preparing HTTP connection pool...")
    def stop(self): print("[RESTEngine] Closing connection pool...")
    def execute(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult:
        print(f"[RESTEngine] Executing {action.action_type.name}")
        return EnvironmentActionResult(status=ActionStatus.SUCCESS, latency=0.0)
