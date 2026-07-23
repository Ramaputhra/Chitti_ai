import time
from desktop.runtimes.environment.adapters.base_adapter import IEnvironmentAdapter
from desktop.models.environment import EnvironmentAction, EnvironmentContext, AdapterHealth, AdapterManifest, ActionType, EnvironmentActionResult, ActionStatus
from desktop.runtimes.environment.adapters.file.engine import IFileEngine, LocalFileEngine

class FileAdapter(IEnvironmentAdapter):
    """
    Translates generic EnvironmentActions (READ, WRITE, LIST, WATCH) into IFileEngine operations.
    Rule 354: Adapter Engine Independence.
    """
    
    def __init__(self, engine: IFileEngine = None):
        self._health = AdapterHealth.OFFLINE
        self.engine = engine or LocalFileEngine()
        self.manifest = AdapterManifest(
            id="file.default",
            version="1.0",
            capabilities=[
                "Read", "Write", "List", "Watch", "Query Metadata", "Stream"
            ],
            permissions=["filesystem.read", "filesystem.write"],
            platforms=["windows", "linux", "mac"]
        )
        
    def initialize(self) -> None:
        self.engine.start()
        self._health = AdapterHealth.READY
        print("[FileAdapter] Initialized via engine")

    def check_health(self) -> AdapterHealth:
        return self._health

    def execute_action(self, action: EnvironmentAction, context: EnvironmentContext) -> EnvironmentActionResult:
        """
        FileAdapter no longer returns boolean. It returns normalized EnvironmentActionResult.
        """
        start_time = time.time()
        
        try:
            if action.action_type == ActionType.WATCH:
                # WATCH is an asynchronous subscription handled by the session, returning SUCCESS immediately
                print(f"[FileAdapter] Emitting event subscription for {action.target.resource_id}")
                result = EnvironmentActionResult(status=ActionStatus.SUCCESS, latency=0.0)
            else:
                result = self.engine.execute(action, context)
        except Exception as e:
            result = EnvironmentActionResult(
                status=ActionStatus.FAILED,
                latency=0.0,
                error=str(e)
            )
            
        # Update latency
        result.latency = (time.time() - start_time) * 1000
        self._record_telemetry(action, result, context)
        return result

    def dispose(self) -> None:
        self.engine.stop()
        self._health = AdapterHealth.OFFLINE
        print("[FileAdapter] Disposed")
        
    def _record_telemetry(self, action: EnvironmentAction, result: EnvironmentActionResult, context: EnvironmentContext):
        print(f"[FileAdapter Telemetry] Target: {action.target.resource_id} | Action: {action.action_type.name} | Status: {result.status.name} | Latency: {result.latency:.2f}ms")
