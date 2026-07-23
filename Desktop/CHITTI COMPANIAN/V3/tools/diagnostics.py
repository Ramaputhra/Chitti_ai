from desktop.models.events import Event

class DiagnosticsObserver:
    """
    Passively monitors the EventBus for developer mode.
    Computes latency using native Started/Completed events, prints live streams,
    and visualizes failure. Outputs interaction trace to JSON log.
    """
    def __init__(self):
        import time
        self.start_times = {}
        self.interaction_events = {}
        self.interaction_summaries = {}
        
        # Ensure logs directory exists
        import os
        self.log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "interactions"))
        os.makedirs(self.log_dir, exist_ok=True)
        
    def attach(self, kernel):
        if hasattr(kernel, "context") and hasattr(kernel.context, "event_bus"):
            kernel.context.event_bus.subscribe(Event, self.handle_event)
            print("[DiagnosticsObserver] Attached to EventBus.")
            
    def handle_event(self, event: Event):
        import time
        import json
        from datetime import datetime
        
        event_type = type(event).__name__
        interaction_id = getattr(event, "interaction_id", None) or getattr(event, "correlation_id", None)
        
        if not interaction_id:
            # Fallback if there's an interaction inside the event
            interaction = getattr(event, "interaction", None)
            if interaction:
                interaction_id = getattr(interaction, "id", None)
                
        if not interaction_id:
            return
            
        # Initialize trace for this interaction
        if interaction_id not in self.interaction_events:
            self.interaction_events[interaction_id] = []
            
        if interaction_id not in self.interaction_summaries:
             self.interaction_summaries[interaction_id] = {
                 "Intent": "Unknown",
                 "Confidence": 0.0,
                 "Planner": "WAITING",
                 "Workflow": "WAITING",
                 "Execution": "WAITING",
                 "Capability": "Unknown",
                 "Result": "PENDING"
             }
             
        summary = self.interaction_summaries[interaction_id]
            
        # Serialize event for tracing
        event_data = {
            "type": event_type,
            "timestamp": event.timestamp.isoformat() if hasattr(event, "timestamp") and isinstance(event.timestamp, datetime) else None,
            "source": getattr(event, "source", getattr(event, "origin", "unknown"))
        }
        self.interaction_events[interaction_id].append(event_data)
        
        # Extract specific data for the summary
        if event_type == "IntentResolved":
            summary["Intent"] = event.result.intent
            summary["Confidence"] = event.result.confidence
        elif event_type == "PlanCreated":
            summary["Planner"] = "PASS"
            summary["Workflow"] = "PASS"
        elif event_type == "ExecutionStartedEvent":
            workflow = getattr(event, "workflow", None)
            if workflow and hasattr(workflow, "capability_id"):
                summary["Capability"] = workflow.capability_id
        elif event_type == "ExecutionCompletedEvent":
            summary["Execution"] = "PASS"
            summary["Result"] = "PASS"
        elif event_type == "ExecutionFailedEvent":
            summary["Execution"] = "FAIL"
            summary["Result"] = "FAIL"
        
        # Live Stream & Timing logic
        if event_type == "InteractionStartedEvent":
            self.start_times[f"{interaction_id}_total"] = time.time()
            self.start_times[f"{interaction_id}_Conversation"] = time.time()
            print(f"\n[Conversation] ✔ Wake Word / Interaction Started")
            
        elif event_type == "InferenceRequested":
            print(f"[Inference] ⏳ Prompt sent to LLM...")
            self.start_times[f"{interaction_id}_Inference"] = time.time()
            
        elif event_type == "InferenceCompleted":
            if f"{interaction_id}_Inference" in self.start_times:
                elapsed = (time.time() - self.start_times[f"{interaction_id}_Inference"]) * 1000
                print(f"[Inference] ✔ Completed [{elapsed:.0f} ms]")
                
        elif event_type == "PlanCreated":
            if f"{interaction_id}_Conversation" in self.start_times:
                elapsed = (time.time() - self.start_times[f"{interaction_id}_Conversation"]) * 1000
                print(f"[Planner] ✔ Intent Resolved [{elapsed:.0f} ms]")
                
            plan = getattr(event, "plan", None)
            if plan and hasattr(plan, "intent"):
                print(f"            > Intent: {plan.intent}")
                print(f"            > Workflows: {len(plan.workflows)}")
                
        elif event_type == "ExecutionStartedEvent":
            self.start_times[f"{interaction_id}_Execution"] = time.time()
            workflow = getattr(event, "workflow", None)
            if workflow:
                print(f"[Execution] ⏳ Launching capability: {workflow.capability_id}...")
                
        elif event_type == "ExecutionCompletedEvent":
            if f"{interaction_id}_Execution" in self.start_times:
                elapsed = (time.time() - self.start_times[f"{interaction_id}_Execution"]) * 1000
                print(f"[Execution] ✔ Completed [{elapsed:.0f} ms]")
                
        elif event_type == "ExecutionFailedEvent":
            print(f"[Execution] ❌ Failed: {getattr(event, 'error', 'Unknown Error')}")
            
        elif event_type == "RecoveryStarted":
            print(f"[Recovery] ⚠️ Initiating recovery sequence...")
            
        elif event_type == "ExpressionDelivered":
            print(f"[Presentation] ✔ Delivered")
            
            # Print Final Summary
            if f"{interaction_id}_total" in self.start_times:
                total_elapsed = (time.time() - self.start_times[f"{interaction_id}_total"])
                
                print("\n━━━━━━━━━━━━━━━━━━━━━━\n")
                print(f"Interaction {interaction_id}")
                print(f"\nIntent\n{summary['Intent']}")
                print(f"\nConfidence\n{summary['Confidence']:.2f}")
                print(f"\nPlanner\n{summary['Planner']}")
                print(f"\nWorkflow\n{summary['Workflow']}")
                print(f"\nExecution\n{summary['Execution']}")
                print(f"\nCapability\n{summary['Capability']}")
                print(f"\nTime\n{total_elapsed:.2f} s")
                print(f"\nResult\n{summary['Result']}")
                print("\n━━━━━━━━━━━━━━━━━━━━━━\n")
                
            # Flush Trace
            trace_file = os.path.join(self.log_dir, f"{interaction_id}.json")
            try:
                with open(trace_file, "w") as f:
                    json.dump(self.interaction_events[interaction_id], f, indent=2)
            except Exception as e:
                print(f"[Diagnostics] Failed to write trace: {e}")
                
            # Cleanup
            keys_to_del = [k for k in self.start_times.keys() if k.startswith(interaction_id)]
            for k in keys_to_del:
                del self.start_times[k]
            if interaction_id in self.interaction_events:
                del self.interaction_events[interaction_id]
            if interaction_id in self.interaction_summaries:
                del self.interaction_summaries[interaction_id]
