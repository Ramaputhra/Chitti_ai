import sys
import os
import asyncio
from datetime import datetime

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if v3_root not in sys.path:
    sys.path.insert(0, v3_root)

from desktop.app.kernel import RuntimeConfiguration, BootManager
from desktop.app.capability_contracts import SimpleCapabilityRegistry
from desktop.app.presentation_contracts import DefaultTextRenderer, MarkdownRenderer
from desktop.models.cognition import ExecutionPlan, WorkflowRequest, ExecutionPolicy, ApprovalRequirement
from desktop.models.events import ExecutionCompletedEvent

async def run_verification():
    print("==========================================================")
    print("Starting COG-31C Canonical Production Verification")
    print("==========================================================\n")
    
    print("[1/5] Booting Canonical Production Architecture...")
    config = RuntimeConfiguration(use_llm=False)
    boot = BootManager(config=config)
    from desktop.runtimes.capability.registry import CapabilityRegistry
    cap_registry = CapabilityRegistry()
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    boot.compose_runtimes(cap_registry, renderers)
    
    success = await boot.initialize()
    if not success:
        print("❌ Boot initialization failed.")
        sys.exit(1)
        
    kernel = await boot.start()
    print("✅ Canonical BootManager reaches READY state.\n")
    
    print("[2/5] Setting up Diagnostics Event Subscriber...")
    events_captured = []
    def on_event(event):
        # We want to catch the specific ExecutionCompletedEvent emitted by ExecutionRuntime
        if event.__class__.__name__ == "Event" and getattr(event, "payload", None) and getattr(event, "event_type", None) == "EXECUTION_COMPLETED":
            events_captured.append(event)
        elif event.__class__.__name__ == "ExecutionCompletedEvent":
            events_captured.append(event)
            
    # Also hook into the generic event handler for logging
    def global_handler(event):
        payload = getattr(event, "payload", {})
        if "event" in payload:
            inner_event = payload["event"]
            if inner_event.__class__.__name__ == "ExecutionCompletedEvent":
                events_captured.append(inner_event)
                
    kernel.context.event_bus.subscribe(ExecutionCompletedEvent, on_event)
    try:
        from desktop.models.events import Event
        kernel.context.event_bus.subscribe(Event, global_handler)
    except:
        pass
    print("✅ Subscribed to ExecutionCompletedEvent.\n")
    
    print("[3/5] Publishing Deterministic ExecutionPlan (TextResponseCapability)...")
    plan = ExecutionPlan(
        approval=ApprovalRequirement(required=False, reason="Verification"),
        workflows=[
            WorkflowRequest(
                action="text_response",
                parameters={"text": "Production Success Path Verification"},
                policy=ExecutionPolicy(timeout=10.0),
                correlation_id="corr_31c"
            )
        ]
    )
    
    # We must push this into the EventBus so that WorkflowRuntime intercepts it.
    kernel.context.event_bus.publish(plan)
    
    print("[4/5] Awaiting Asynchronous Orchestration...")
    # Allow async loop to process the plan
    for _ in range(20):
        await asyncio.sleep(0.1)
        
    print("\n[5/5] Analyzing Observability Contracts...")
    print(f"Captured {len(events_captured)} ExecutionCompletedEvent(s).")
    
    all_passed = True
    
    if len(events_captured) == 0:
        print("❌ FAILED: ExecutionCompletedEvent was not emitted.")
        all_passed = False
    else:
        print("✅ SUCCESS: ExecutionCompletedEvent emitted.")
        event = events_captured[0]
        metadata = getattr(event, "metadata", {}) if hasattr(event, "metadata") else event.payload.get("metadata", {})
        trace = metadata.get("execution_trace")
        
        if not trace:
            print("❌ FAILED: ExecutionCompletedEvent does not carry ExecutionTrace.")
            all_passed = False
        else:
            print("✅ SUCCESS: ExecutionTrace object is present in event.")
            
            steps = getattr(trace, "steps", [])
            if not steps or len(steps) == 0:
                print("❌ FAILED: ExecutionTrace does not contain ExecutionStep records.")
                all_passed = False
            else:
                print(f"✅ SUCCESS: ExecutionTrace contains {len(steps)} ExecutionStep record(s).")
                
    print("\n==========================================================")
    if all_passed:
        print("DECISION: COG-31C CERTIFIED")
    else:
        print("DECISION: COG-31C NOT CERTIFIED")
    print("==========================================================")
    
    await kernel.shutdown()

if __name__ == "__main__":
    asyncio.run(run_verification())
