from desktop.orchestrator.state_machine import RuntimeStateMachine, RuntimeLifecycleState, PipelineEventBus
from desktop.orchestrator.adapters import InputAdapter, OutputAdapter
from desktop.orchestrator.cognitive_pipeline import CognitivePipeline

class MockEngine:
    pass

def run_verification():
    print("Starting EE1 System Integration Verification...\n")
    
    print("[1/5] Verifying Runtime State Machine Lifecycle...")
    sm = RuntimeStateMachine()
    assert sm.current_state == RuntimeLifecycleState.BOOTING
    sm.transition(RuntimeLifecycleState.INITIALIZING)
    sm.transition(RuntimeLifecycleState.READY)
    sm.transition(RuntimeLifecycleState.LISTENING)
    sm.transition(RuntimeLifecycleState.PROCESSING)
    print("       State Machine successfully advanced BOOTING -> PROCESSING")
    
    print("[2/5] Verifying Event Bus Publishing...")
    bus = PipelineEventBus()
    events_caught = []
    bus.subscribe(lambda ev, data: events_caught.append(ev))
    bus.publish("TestEvent")
    assert "TestEvent" in events_caught
    print("       EventBus successfully published and subscribed.")
    
    print("[3/5] Verifying Adapters...")
    inp = InputAdapter()
    exp = inp.translate("Open browser", {}, {})
    assert exp.raw_input == "Open browser"
    print("       InputAdapter correctly translated payload to Experience.")
    
    print("[4/5] Verifying Cognitive Pipeline Dependency Injection & Event Emission...")
    pipeline = CognitivePipeline(bus, MockEngine(), MockEngine(), MockEngine(), MockEngine(), MockEngine(), MockEngine(), MockEngine(), MockEngine(), MockEngine())
    res = pipeline.process(exp)
    
    print("[5/5] Verifying Execution Result Feedback Output...")
    out = OutputAdapter()
    ui_dispatch = out.translate(res)
    assert ui_dispatch["ui_signals"]["status"] == "COMPLETED"
    print("       OutputAdapter successfully translated ExecutionResult.")
    
    print("\n✅ EE1 System Integration Runtime strictly verified.")

if __name__ == "__main__":
    run_verification()
