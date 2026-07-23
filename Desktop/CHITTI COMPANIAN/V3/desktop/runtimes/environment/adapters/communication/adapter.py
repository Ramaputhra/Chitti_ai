import time
from desktop.runtimes.environment.adapters.base_adapter import IEnvironmentAdapter
from desktop.models.environment import EnvironmentAction, EnvironmentContext, AdapterHealth, AdapterManifest, ActionType, EnvironmentActionResult, ActionStatus
from desktop.runtimes.environment.adapters.communication.engine import IEmailEngine, SMTPEngine, ICalendarEngine, GoogleCalendarEngine, IAPIEngine, RESTEngine

class EmailAdapter(IEnvironmentAdapter):
    def __init__(self, engine: IEmailEngine = None):
        self._health = AdapterHealth.OFFLINE
        self.engine = engine or SMTPEngine()
        self.manifest = AdapterManifest(
            id="email.default", version="1.0",
            capabilities=["Send", "Reply", "Forward", "Read", "Attachments", "Watch Inbox"],
            permissions=["email.read", "email.send"], platforms=["all"]
        )
    def initialize(self) -> None:
        self.engine.start(); self._health = AdapterHealth.READY
    def check_health(self) -> AdapterHealth: return self._health
    def execute_action(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult:
        start_time = time.time()
        try:
            if action.action_type in (ActionType.WATCH, ActionType.SUBSCRIBE):
                print(f"[EmailAdapter] Emitting event subscription for {action.target.resource_id}")
                result = EnvironmentActionResult(status=ActionStatus.SUCCESS, latency=0.0)
            else:
                result = self.engine.execute(action, context)
        except Exception as e:
            result = EnvironmentActionResult(status=ActionStatus.FAILED, latency=0.0, error=str(e))
        result.latency = (time.time() - start_time) * 1000
        print(f"[EmailAdapter Telemetry] Action: {action.action_type.name} | Status: {result.status.name}")
        return result
    def dispose(self) -> None: self.engine.stop()

class CalendarAdapter(IEnvironmentAdapter):
    def __init__(self, engine: ICalendarEngine = None):
        self._health = AdapterHealth.OFFLINE
        self.engine = engine or GoogleCalendarEngine()
        self.manifest = AdapterManifest(
            id="calendar.default", version="1.0",
            capabilities=["List Events", "Create Event", "Watch Calendar", "Respond to Invite"],
            permissions=["calendar.read", "calendar.write"], platforms=["all"]
        )
    def initialize(self) -> None:
        self.engine.start(); self._health = AdapterHealth.READY
    def check_health(self) -> AdapterHealth: return self._health
    def execute_action(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult:
        start_time = time.time()
        try:
            if action.action_type in (ActionType.WATCH, ActionType.SUBSCRIBE):
                result = EnvironmentActionResult(status=ActionStatus.SUCCESS, latency=0.0)
            else:
                result = self.engine.execute(action, context)
        except Exception as e:
            result = EnvironmentActionResult(status=ActionStatus.FAILED, latency=0.0, error=str(e))
        result.latency = (time.time() - start_time) * 1000
        return result
    def dispose(self) -> None: self.engine.stop()

class APIAdapter(IEnvironmentAdapter):
    def __init__(self, engine: IAPIEngine = None):
        self._health = AdapterHealth.OFFLINE
        self.engine = engine or RESTEngine()
        self.manifest = AdapterManifest(
            id="api.default", version="1.0",
            capabilities=["REST", "GraphQL", "Webhooks", "SSE Streaming"],
            permissions=["network.external"], platforms=["all"]
        )
    def initialize(self) -> None:
        self.engine.start(); self._health = AdapterHealth.READY
    def check_health(self) -> AdapterHealth: return self._health
    def execute_action(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult:
        start_time = time.time()
        try:
            if action.action_type in (ActionType.STREAM, ActionType.SUBSCRIBE):
                result = EnvironmentActionResult(status=ActionStatus.SUCCESS, latency=0.0)
            else:
                result = self.engine.execute(action, context)
        except Exception as e:
            result = EnvironmentActionResult(status=ActionStatus.FAILED, latency=0.0, error=str(e))
        result.latency = (time.time() - start_time) * 1000
        return result
    def dispose(self) -> None: self.engine.stop()
