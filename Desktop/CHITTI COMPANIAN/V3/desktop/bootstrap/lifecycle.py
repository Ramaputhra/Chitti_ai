import traceback

class HealthState:
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    RECOVERING = "RECOVERING"
    UNAVAILABLE = "UNAVAILABLE"

class LifecycleState:
    PRE_INIT = "PRE_INIT"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    SHUTTING_DOWN = "SHUTTING_DOWN"
    TERMINATED = "TERMINATED"
    CRASHED = "CRASHED"

class ShutdownManager:
    def __init__(self, registry):
        self.registry = registry

    def shutdown(self):
        print("[ShutdownManager] Initiating graceful shutdown...")
        services = sorted(self.registry.get_all(), key=lambda s: s.shutdown_order, reverse=True)
        for srv in services:
            try:
                if hasattr(srv.instance, 'stop'):
                    srv.instance.stop()
            except Exception as e:
                print(f"Error shutting down {srv.identifier}: {e}")
        print("[ShutdownManager] Shutdown complete.")

class LifecycleManager:
    def __init__(self, registry):
        self.state = LifecycleState.PRE_INIT
        self.registry = registry
        self.shutdown_manager = ShutdownManager(registry)
        
    def transition(self, new_state):
        self.state = new_state
        
    def handle_crash(self, exception):
        self.state = LifecycleState.CRASHED
        with open("startup_diagnostics.log", "w") as f:
            f.write("CRASH LOG\n")
            f.write(traceback.format_exc())
        print("[LifecycleManager] Fatal crash detected. Logs dumped.")
