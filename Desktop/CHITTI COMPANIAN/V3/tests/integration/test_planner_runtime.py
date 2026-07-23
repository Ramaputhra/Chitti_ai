import logging
from typing import Dict, Any

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

from desktop.platform.components.capabilities.open_folder_manifest import get_open_folder_manifest
from desktop.platform.ai.capability_resolver import CapabilityResolver
from desktop.platform.ai.planner_runtime import PlannerRuntime
from desktop.platform.core.runtime_kernel import RuntimeKernel
from desktop.models.semantic_models import DesktopIntent, IntentType, IntentGeneratedEvent
from desktop.models.planner_models import PlanFailureReason

def run_planner_test():
    logging.basicConfig(level=logging.INFO)
    print("\n--- Running Decide & Plan Integration Tests ---")
    
    bus = MockEventBus()
    
    # Setup capability registry
    registry = [get_open_folder_manifest()]
    
    resolver = CapabilityResolver(registry)
    planner = PlannerRuntime()
    kernel = RuntimeKernel(bus, resolver, planner)
    
    def get_published_types():
        return [e[0] for e in bus.published_events]
        
    def get_last_event_payload():
        return bus.published_events[-1][1]["event"]
        
    # --- 1. Resolution Test (Happy Path) ---
    print("\n[TEST 1: Golden Path - Open Downloads]")
    intent = DesktopIntent(
        action=IntentType.OPEN,
        target="Downloads",
        object_type="folder",
        session_id="session-123"
    )
    event = IntentGeneratedEvent(desktop_intent=intent, timestamp=1.0, session_id="session-123")
    
    bus.publish("INTENT_GENERATED", "Semantic", payload={"event": event})
    
    types = get_published_types()
    assert "CAPABILITY_RESOLVED" in types
    assert "EXECUTION_PLAN_CREATED" in types
    
    plan_event = get_last_event_payload()
    assert plan_event.plan.intent_id == "session-123"
    assert len(plan_event.plan.steps) == 1
    assert plan_event.plan.steps[0].capability_id == "sys.folder.open"
    assert plan_event.plan.steps[0].parameters["folder_path"] == "Downloads"
    print("✅ Success: Intent successfully mapped to capability and immutable plan generated.")

    # --- 2. Missing Capability Test ---
    print("\n[TEST 2: Unknown Capability]")
    bus.published_events.clear()
    
    intent = DesktopIntent(
        action=IntentType.FLY, # Not in our registry
        target="Moon",
        session_id="session-456"
    )
    # Patch the Enum dynamically for this test since FLY isn't in IntentType
    from types import SimpleNamespace
    intent.action = SimpleNamespace(name="FLY")
    
    event = IntentGeneratedEvent(desktop_intent=intent, timestamp=1.0, session_id="session-456")
    bus.publish("INTENT_GENERATED", "Semantic", payload={"event": event})
    
    types = get_published_types()
    assert "CAPABILITY_RESOLVED" not in types
    assert "EXECUTION_PLAN_FAILED" in types
    
    fail_event = get_last_event_payload()
    assert fail_event.reason == PlanFailureReason.UNKNOWN_CAPABILITY
    print("✅ Success: Unknown capability cleanly rejected by Resolver.")

    # --- 3. Missing Parameter Test ---
    print("\n[TEST 3: Missing Required Parameter]")
    bus.published_events.clear()
    
    intent = DesktopIntent(
        action=IntentType.OPEN,
        target=None, # Missing the target/folder_path parameter
        object_type="folder",
        session_id="session-789"
    )
    event = IntentGeneratedEvent(desktop_intent=intent, timestamp=1.0, session_id="session-789")
    bus.publish("INTENT_GENERATED", "Semantic", payload={"event": event})
    
    types = get_published_types()
    assert "CAPABILITY_RESOLVED" in types # It matched OPEN
    assert "EXECUTION_PLAN_FAILED" in types # But failed to plan
    
    fail_event = get_last_event_payload()
    assert fail_event.reason == PlanFailureReason.MISSING_PARAMETER
    print("✅ Success: Planner safely rejected generation due to missing parameter.")

if __name__ == "__main__":
    run_planner_test()
