import time
from desktop.runtimes.environment.adapters.base_adapter import IEnvironmentAdapter
from desktop.models.environment import EnvironmentAction, EnvironmentContext, AdapterHealth, AdapterManifest, ActionType, EnvironmentActionResult, ActionStatus
from desktop.runtimes.environment.adapters.ide.engine import IIDEEngine, VSCodeEngine

class IDEAdapter(IEnvironmentAdapter):
    """
    The Developer Workspace Adapter.
    Translates generic actions (OPEN_RESOURCE, FOCUS, ATTACH, READ_RESOURCE, STREAM) into IIDEEngine ops.
    """
    
    def __init__(self, engine: IIDEEngine = None):
        self._health = AdapterHealth.OFFLINE
        self.engine = engine or VSCodeEngine()
        self.manifest = AdapterManifest(
            id="ide.default",
            version="1.0",
            capabilities=[
                "Editing", "Terminal", "Git", "Debugging", "Language Server", 
                "Tasks", "Extensions", "Formatting", "Search", "Refactoring"
            ],
            permissions=["workspace.read", "workspace.write", "terminal.execute"],
            platforms=["windows", "linux", "mac"]
        )
        
    def initialize(self) -> None:
        self.engine.start()
        self._health = AdapterHealth.READY
        print("[IDEAdapter] Initialized via engine")

    def check_health(self) -> AdapterHealth:
        return self._health

    def execute_action(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult:
        start_time = time.time()
        
        try:
            if action.action_type == ActionType.STREAM:
                # Streaming support (terminals, build logs, diagnostics) via EnvironmentArtifact
                print(f"[IDEAdapter] Initializing stream for {action.target.resource_id}")
                result = EnvironmentActionResult(status=ActionStatus.SUCCESS, latency=0.0)
            else:
                result = self.engine.execute(action, context)
        except Exception as e:
            result = EnvironmentActionResult(
                status=ActionStatus.FAILED,
                latency=0.0,
                error=str(e)
            )
            
        result.latency = (time.time() - start_time) * 1000
        self._record_telemetry(action, result, context)
        return result

    def dispose(self) -> None:
        self.engine.stop()
        self._health = AdapterHealth.OFFLINE
        print("[IDEAdapter] Disposed")
        
    def _record_telemetry(self, action: EnvironmentAction, result: EnvironmentActionResult, context: EnvironmentContext):
        # extended telemetry for diagnostics and future automation patterns
        print(f"[IDEAdapter Telemetry] Target: {action.target.resource_id} | Action: {action.action_type.name} | Status: {result.status.name} | Latency: {result.latency:.2f}ms")
