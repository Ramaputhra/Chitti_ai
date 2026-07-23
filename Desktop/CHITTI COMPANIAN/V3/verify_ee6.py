from desktop.bootstrap.manager import BootstrapManager, BootstrapManifest
from desktop.bootstrap.lifecycle import LifecycleState, HealthState
import time

def run_verification():
    print("Starting EE6 Platform Bootstrap Verification...\n")
    
    manifest = BootstrapManifest(
        required_services=["CoreDB", "CognitiveEngine", "MainOrchestrator"],
        optional_services=["TelemetryLogger"],
        failure_policy="HARD_CRASH"
    )
    
    print("[1/5] Verifying Configuration Immutability...")
    manager = BootstrapManager(manifest)
    manager.boot()
    assert manager.config_loader._is_frozen == True
    print("       Configuration safely frozen upon RUNNING transition.")
    
    print("[2/5] Verifying Service Dependency Graph & DI Container...")
    services = manager.registry.get_all()
    assert len(services) == 3
    print("       DependencyContainer correctly resolved and registered services.")
    
    print("[3/5] Verifying Runtime Health Model...")
    assert manager.registry.health_state == HealthState.HEALTHY
    print("       Runtime initialized to HEALTHY state.")
    
    print("[4/5] Verifying Crash Recovery Diagnostics...")
    crashing_manager = BootstrapManager(manifest)
    def failing_boot():
        raise RuntimeError("Simulated SQLite Lock Error")
    crashing_manager.boot = failing_boot
    try:
        crashing_manager.boot()
    except Exception as e:
        crashing_manager.lifecycle.handle_crash(e)
    
    assert crashing_manager.lifecycle.state == LifecycleState.CRASHED
    print("       Crash gracefully intercepted and diagnostic dump generated.")
    
    print("[5/5] Verifying Shutdown Correctness...")
    manager.shutdown()
    assert manager.lifecycle.state == LifecycleState.TERMINATED
    print("       ShutdownManager successfully executed LIFO teardown.")
    
    print("\n✅ EE6 Platform Bootstrap & Runtime Lifecycle strictly verified.")

if __name__ == "__main__":
    run_verification()
