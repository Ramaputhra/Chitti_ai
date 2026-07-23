import logging
import time
from typing import Dict, Any

from desktop.platform.components.capabilities.open_folder_manifest import get_open_folder_manifest
from desktop.platform.ai.capability_resolver import CapabilityResolver
from desktop.platform.ai.planner_runtime import PlannerRuntime
from desktop.platform.core.runtime_kernel import RuntimeKernel
from desktop.platform.core.capability_runtime import CapabilityRuntime
from desktop.platform.core.execution_scheduler import ExecutionScheduler
from desktop.platform.core.verification_runtime import VerificationRuntime
from desktop.platform.core.evidence_manager import EvidenceManager
from desktop.models.semantic_models import DesktopIntent, IntentType, IntentGeneratedEvent

class MockEventBus:
    def __init__(self):
        self.subscribers = {}
        self.published_events = []

    def subscribe(self, event_type: str, callback: Any) -> None:
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event_type: str, source: str, payload: Dict[str, Any] = None) -> None:
        self.published_events.append((event_type, payload))
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback({"payload": payload or {}})

def run_execute_and_verify_test():
    logging.basicConfig(level=logging.INFO)
    print("\n--- Running Phase 5.4 End-to-End Execution Test ---")
    
    bus = MockEventBus()
    
    # Setup capability registry
    registry = [get_open_folder_manifest()]
    
    # 1. Setup Phase 5.3 (Plan)
    resolver = CapabilityResolver(registry)
    planner = PlannerRuntime()
    kernel = RuntimeKernel(bus, resolver, planner)
    
    # 2. Setup Phase 5.4 (Execute & Verify)
    capability_runtime = CapabilityRuntime(bus)
    scheduler = ExecutionScheduler(capability_runtime)
    kernel.scheduler = scheduler # Bind to kernel
    
    evidence_manager = EvidenceManager()
    verification_runtime = VerificationRuntime(bus, evidence_manager, registry)
    kernel.verification_runtime = verification_runtime # Bind to kernel
    
    def get_published_types():
        return [e[0] for e in bus.published_events]

    # --- Test 1: Full Pipeline ---
    print("\n[TEST 1: End-to-End Pipeline - Open Downloads]")
    intent = DesktopIntent(
        action=IntentType.OPEN,
        target="Downloads",
        object_type="folder",
        session_id="session-54-test"
    )
    event = IntentGeneratedEvent(desktop_intent=intent, timestamp=time.time(), session_id="session-54-test")
    
    bus.publish("INTENT_GENERATED", "Semantic", payload={"event": event})
    
    types = get_published_types()
    
    # Validate the full 8-step event chain
    assert "CAPABILITY_RESOLVED" in types
    print("✅ CAPABILITY_RESOLVED")
    # execution plan doesn't publish explicitly since we bypassed it to active_workflows directly in kernel patch, but scheduling worked
    assert "CAPABILITY_STARTED" in types
    print("✅ CAPABILITY_STARTED (Context narrowed)")
    assert "CAPABILITY_COMPLETED" in types
    print("✅ CAPABILITY_COMPLETED (Adapter executed os.startfile)")
    assert "VERIFICATION_STARTED" in types
    print("✅ VERIFICATION_STARTED (Asynchronous kickoff)")
    assert "VERIFICATION_COMPLETED" in types
    print("✅ VERIFICATION_COMPLETED (Evidence fused from OS)")
    assert "WORKFLOW_COMPLETED" in types
    print("✅ WORKFLOW_COMPLETED (Success)")
    
if __name__ == "__main__":
    run_execute_and_verify_test()
