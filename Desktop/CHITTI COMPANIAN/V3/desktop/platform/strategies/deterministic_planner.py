from uuid import uuid4
from desktop.app.planner_contracts import IPlannerStrategy
from desktop.models.interaction import InteractionEnvelope, IntentResolved
from desktop.models.memory import MemorySnapshot
from desktop.models.cognition import Intent, ConversationIntent, SystemIntent, PlanningDecision, ExecutionPlan, WorkflowRequest, ApprovalRequirement, ExecutionPolicy, RetryPolicy

class DeterministicPlannerStrategy(IPlannerStrategy):
    """
    Sprint 79 Implementation: A rules-based strategy to prove the cognitive pipeline.
    """
    def __init__(self, catalog=None):
        self.version = "1.0.0-deterministic"
        self.catalog = catalog

    def parse_intent(self, event: IntentResolved, context: MemorySnapshot) -> Intent:
        result = event.result
        
        if result.intent in ("SystemCommand", "CommandIntent"):
            return ConversationIntent(
                subtype="CommandIntent", 
                query=result.parameters.get("action", result.parameters.get("command", "unknown")),
                parameters=result.parameters
            )

        elif result.intent == "DistanceIntent":
            return ConversationIntent(subtype="DistanceIntent", query=result.parameters.get("query", ""), parameters=result.parameters)
        elif result.intent == "ShowMeIntent":
            return ConversationIntent(subtype="ShowMeIntent", query=result.parameters.get("query", ""), parameters=result.parameters)
        elif result.intent == "LaunchAppIntent":
            return ConversationIntent(subtype="LaunchAppIntent", query=result.parameters.get("app_command", ""), parameters=result.parameters)
        elif result.intent == "CloseAppIntent":
            return ConversationIntent(subtype="CloseAppIntent", query=result.parameters.get("app_command", ""), parameters=result.parameters)
        elif result.intent == "OpenBrowserIntent":
            return ConversationIntent(subtype="OpenBrowserIntent", query=result.parameters.get("query", ""), parameters=result.parameters)
        elif result.intent == "ResumeActivityIntent":
            return ConversationIntent(subtype="ResumeActivityIntent", query=result.parameters.get("query", ""), parameters=result.parameters)

        elif result.intent == "StateQueryIntent":
            return ConversationIntent(
                subtype="StateQueryIntent",
                query=result.parameters.get("action", result.parameters.get("query", "unknown")),
                parameters=result.parameters
            )

        else:
            return ConversationIntent(subtype="UnknownIntent", query=str(result.parameters), parameters=result.parameters)

    def formulate_decision(self, intent: Intent, context: MemorySnapshot) -> PlanningDecision:
        workflows = []
        approval = ApprovalRequirement(required=False)
        
        if isinstance(intent, SystemIntent):
            pass # Replaced by CommandIntent
        
        elif isinstance(intent, ConversationIntent):
            corr_id = str(uuid4()) # In real implementation, pass interaction.correlation_id
            
            if intent.subtype == "CommandIntent":
                action = intent.query
                descriptor = self.catalog.resolve_action(None, action) if self.catalog else None
                if descriptor:
                    workflows.append(WorkflowRequest(
                        action=descriptor.id, 
                        correlation_id=corr_id,
                        parameters=intent.parameters,
                        policy=ExecutionPolicy(timeout=10.0, retry_policy=RetryPolicy.NONE)
                    ))
                else:
                    workflows.append(WorkflowRequest(
                        action="TextResponseCapability",
                        correlation_id=corr_id,
                        parameters={"text": f"I don't know how to perform the action: {action}."},
                        policy=ExecutionPolicy(timeout=2.0, retry_policy=RetryPolicy.NONE)
                    ))
            elif intent.subtype == "LaunchAppIntent":
                workflows.append(WorkflowRequest(
                    action="LaunchApplicationCapability",
                    correlation_id=corr_id,
                    parameters={"app_command": intent.query, "arguments": []},
                    policy=ExecutionPolicy(timeout=10.0, retry_policy=RetryPolicy.NONE)
                ))
                workflows.append(WorkflowRequest(
                    action="TextResponseCapability",
                    correlation_id=corr_id,
                    parameters={"text": f"Opened {intent.query}."},
                    policy=ExecutionPolicy(timeout=2.0, retry_policy=RetryPolicy.NONE)
                ))
            elif intent.subtype == "CloseAppIntent":
                app_name = intent.query
                if not app_name.endswith(".exe"):
                    app_name += ".exe"
                workflows.append(WorkflowRequest(
                    action="ExecuteTerminalCommandCapability",
                    correlation_id=corr_id,
                    parameters={
                        "command": "taskkill",
                        "arguments": ["/IM", app_name, "/F"],
                        "cwd": "C:\\"
                    },
                    policy=ExecutionPolicy(timeout=10.0, retry_policy=RetryPolicy.NONE)
                ))
                workflows.append(WorkflowRequest(
                    action="TextResponseCapability",
                    correlation_id=corr_id,
                    parameters={"text": f"Closed {intent.query}."},
                    policy=ExecutionPolicy(timeout=2.0, retry_policy=RetryPolicy.NONE)
                ))

            elif intent.subtype == "DistanceIntent":
                # Route to DistanceCapability (Hero Scenario)
                words = intent.query.split(" to ")
                destination = "Ameerpet"
                if len(words) > 1:
                    destination = words[-1].replace("?", "").strip().title()
                    
                workflows.append(WorkflowRequest(
                    action="DistanceCapability", 
                    correlation_id=corr_id,
                    parameters={"origin": "here", "destination": destination},
                    policy=ExecutionPolicy(timeout=2.0, retry_policy=RetryPolicy.NONE)
                ))
                workflows.append(WorkflowRequest(
                    action="TextResponseCapability", 
                    correlation_id=corr_id,
                    parameters={"text": f"The distance to {destination} is 6.2 kilometers. It should take about 18 minutes right now."},
                    policy=ExecutionPolicy(timeout=2.0, retry_policy=RetryPolicy.NONE)
                ))
            elif intent.subtype == "ShowMeIntent":
                # Multi-turn Context Reuse
                has_card = False
                if hasattr(context, "episodes"):
                    for ep in reversed(context.episodes):
                        if hasattr(ep, "metadata") and "capability_result" in ep.metadata:
                            result = ep.metadata["capability_result"]
                            if hasattr(result, "template_name") and result.template_name == "DistanceCard":
                                has_card = True
                                break
                                
                if has_card:
                    workflows.append(WorkflowRequest(
                        action="RenderResultCapability", 
                        correlation_id=corr_id,
                        parameters={"action": "RENDER_CARD"},
                        policy=ExecutionPolicy(timeout=2.0, retry_policy=RetryPolicy.NONE)
                    ))
                else:
                    workflows.append(WorkflowRequest(
                        action="TextResponseCapability", 
                        correlation_id=corr_id,
                        parameters={"text": "I don't have a previous result to display yet."},
                        policy=ExecutionPolicy(timeout=2.0, retry_policy=RetryPolicy.NONE)
                    ))
            elif intent.subtype == "OpenBrowserIntent":
                # Multi-turn Context Reuse: extract URL from MemorySnapshot
                # We look backwards through episodes for a DistanceResult
                url = None
                if hasattr(context, "episodes"):
                    for ep in reversed(context.episodes):
                        if hasattr(ep, "metadata") and "capability_result" in ep.metadata:
                            result = ep.metadata["capability_result"]
                            if hasattr(result, "template_name") and result.template_name == "DistanceCard":
                                if hasattr(result, "template_data"):
                                    url = result.template_data.get("map_url", url)
                                break
                
                if url:
                    workflows.append(WorkflowRequest(
                        action="ExecuteResultActionCapability", 
                        correlation_id=corr_id,
                        parameters={"action": "OPEN_URL", "url": url},
                        policy=ExecutionPolicy(timeout=2.0, retry_policy=RetryPolicy.NONE)
                    ))
                else:
                    workflows.append(WorkflowRequest(
                        action="TextResponseCapability", 
                        correlation_id=corr_id,
                        parameters={"text": "I couldn't find a URL to open."},
                        policy=ExecutionPolicy(timeout=2.0, retry_policy=RetryPolicy.NONE)
                    ))
            elif intent.subtype == "ResumeActivityIntent":
                # Route to ResumeActivityCapability using Genuine ActivityMemory
                # We instantiate ActivityResolver here to keep interface clean for MVP
                # In full V2, ActivityResolver would be injected.
                from desktop.runtimes.activity.resolver import ActivityResolver
                from desktop.runtimes.activity.validator import ActivityValidator
                from desktop.runtimes.memory_runtime import MemoryRuntime
                from desktop.app.context import KernelContext
                
                # Try to get the real memory runtime to fetch activity
                activity = None
                # We assume the caller passed the memory runtime in the snapshot temporarily for this sprint
                memory_runtime = getattr(context, '_memory_runtime', None)
                if not memory_runtime:
                    # Fallback lookup if not passed (for tests)
                    memory_runtime = MemoryRuntime()
                    
                resolver = ActivityResolver(memory_runtime)
                validator = ActivityValidator()
                
                raw_activity = resolver.get_latest_project()
                activity = validator.validate(raw_activity)
                
                if not activity or activity.resume_confidence < 0.5:
                    # Recovery Clarification Workflow
                    reason = "No recent coding activity was found." if not activity else "I found your last project, but it appears to have been moved or is no longer available."
                    workflows.append(WorkflowRequest(
                        action="TextResponseCapability",
                        correlation_id=corr_id,
                        parameters={"text": f"{reason} Would you like to:\n• Open a folder\n• Choose a previous project\n• Create a new project?"},
                        policy=ExecutionPolicy(timeout=2.0, retry_policy=RetryPolicy.NONE)
                    ))
                elif 0.5 <= activity.resume_confidence <= 0.8:
                    # Confirmation Workflow
                    workflows.append(WorkflowRequest(
                        action="TextResponseCapability",
                        correlation_id=corr_id,
                        parameters={"text": f"I found your '{activity.project_name}' project, but some tools aren't running. Should I try resuming it anyway?"},
                        policy=ExecutionPolicy(timeout=2.0, retry_policy=RetryPolicy.NONE)
                    ))
                else:
                    # Confident Resume
                    workflows.append(WorkflowRequest(
                        action="ResumeActivityCapability", 
                        correlation_id=corr_id,
                        parameters={
                            "profile_name": activity.application,
                            "workspace_path": activity.workspace_path,
                            "editor_command": "code",
                            "editor_args": ["."],
                            "start_command": activity.launch_command,
                            "start_args": [],
                            "startup_timeout_sec": 20,
                            "launch_url": activity.browser_url,
                            "verification": activity.verification
                        },
                        policy=ExecutionPolicy(timeout=120.0, retry_policy=RetryPolicy.NONE)
                    ))
            elif intent.subtype == "StateQueryIntent":
                action = intent.query
                descriptor = self.catalog.resolve_action(None, action) if self.catalog else None
                if descriptor:
                    workflows.append(WorkflowRequest(
                        action=descriptor.id, 
                        correlation_id=corr_id,
                        parameters=intent.parameters,
                        policy=ExecutionPolicy(timeout=10.0, retry_policy=RetryPolicy.NONE)
                    ))
        
        plan = ExecutionPlan(
            intent=intent,
            workflows=workflows,
            approval=approval
        )
        return PlanningDecision(plan=plan)

    def create_plan(self, decision: PlanningDecision, event: IntentResolved, session_id: str) -> ExecutionPlan:
        plan = decision.plan
        plan.plan_id = str(uuid4())
        plan.correlation_id = event.correlation_id
        plan.interaction_id = event.result.interaction_id if event.result else ""
        plan.session_id = session_id
        plan.planner_version = self.version
        return plan
