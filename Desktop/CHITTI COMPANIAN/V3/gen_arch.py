import os

base_dir = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\architecture"
decisions_dir = os.path.join(base_dir, "decisions")

os.makedirs(decisions_dir, exist_ok=True)

# Boilerplate for all specifications
boilerplate = """
> **1. The architecture must remain deterministic by default. AI reasoning is an optional capability, never a mandatory dependency for system operation. Any feature that can be executed through deterministic logic must not require an LLM.**
>
> **2. Every runtime must be independently testable, restartable, and replaceable without requiring changes to unrelated runtimes.**

## 1. Purpose
{purpose}

## 2. Responsibilities
{responsibilities}

## 3. Interfaces
- Version 1: {v1_interface}
- Version 2: {v2_interface}
- Final: {final_interface}

## 4. Events
{events}

## 5. Dependencies
{dependencies}

## 6. Failure Modes
{failure_modes}

## 7. Lifecycle
{lifecycle}

## 8. Future Extensions
{future}

## 9. Out of Scope
{out_of_scope}
"""

def generate_spec(title, purpose, resp, v1, v2, final, events, deps, failure, lifecycle, future, out_scope):
    content = f"# {title}\n"
    content += boilerplate.format(
        purpose=purpose, responsibilities=resp, v1_interface=v1, v2_interface=v2, final_interface=final,
        events=events, dependencies=deps, failure_modes=failure, lifecycle=lifecycle, future=future, out_of_scope=out_scope
    )
    return content

docs = {
    "RUNTIME_SPEC.md": generate_spec("Base Runtime Specification", "Base class for all runtimes.", "Lifecycle methods, health state.", "IRuntime", "IRuntime v2", "IRuntime Final", "RuntimeStateChanged", "KernelContext", "Crash", "Created -> Initializing -> Running -> Paused -> Stopping -> Stopped -> Restarting -> Failed", "Containerized runtimes", "Specific capability execution"),
    "SUPERVISOR_SPEC.md": generate_spec("Supervisor Specification", "Manages individual runtimes.", "Restarting, isolating faults.", "None", "Basic Supervisor", "Advanced Supervisor", "RuntimeRestarted", "Runtimes", "Supervisor crash", "Persistent", "Cluster supervision", "Domain logic"),
    "BOOT_SEQUENCE.md": generate_spec("Boot Sequence Specification", "Defines strict startup order.", "Ensure dependencies are loaded before consumers.", "Hardcoded", "Config driven", "Dependency Graph sorted", "SystemBooted", "All core services", "Deadlock", "One-time execution", "Fast-resume", "Runtime logic"),
    "THREADING_MODEL.md": generate_spec("Threading Model Specification", "Rules for concurrency.", "Isolate IO, CPU, and Event processing.", "Asyncio main loop", "Worker pools", "Isolated processes", "ThreadStarved", "OS Threading", "Deadlocks", "Application lifespan", "Multiprocessing", "Business logic"),
    "DOMAIN_MODEL_SPEC.md": generate_spec("Domain Model Specification", "Immutable records passing through the system.", "Data definition.", "Dicts", "Versioned Pydantic", "Schema Registry", "None", "None", "Validation Error", "Ephemeral", "Protobufs", "Behavioral logic"),
    "EVENT_SPEC.md": generate_spec("Event Specification", "Message contracts for the Event Bus.", "Ensure loose coupling with strong contracts.", "Basic Event", "Versioned Event", "Strict Schema Event", "Domain Events", "Domain Models", "Schema Mismatch", "Ephemeral", "Event Sourcing", "Execution logic"),
    "ERROR_MODEL_SPEC.md": generate_spec("Error Model Specification", "Unifies system errors.", "Standardize fatal, retryable, timeout errors.", "Exceptions", "Error Enums", "Rich Error Objects", "ErrorOccurred", "None", "Uncaught exception", "Ephemeral", "Error analytics", "Happy path logic"),
    "INTERACTION_RUNTIME_SPEC.md": generate_spec("Interaction Runtime Specification", "Transport abstraction and input normalization.", "Session creation, auth, normalization.", "Direct input", "Transport abstraction", "Multi-modal multiplexer", "InteractionReceived", "Transports", "Auth failure", "Created -> ... -> Stopped", "Continuous stream", "Intent parsing"),
    "SESSION_SPEC.md": generate_spec("Session Specification", "Defines long-running interaction states.", "Manage conversational context and timeouts.", "Basic ID mapping", "Idle timeouts", "Complex graphs", "SessionStateChanged", "Memory", "Session corruption", "Created -> Active -> Idle -> Stopped", "Cross-device", "Execution logic"),
    "INTENT_RUNTIME_SPEC.md": generate_spec("Intent Runtime Specification", "Normalizes natural language to typed intents.", "Slot filling, matching.", "Regex", "Basic Semantic", "Advanced NLP Gateway", "IntentRecognized", "AI Gateway", "Misclassification", "Created -> ... -> Stopped", "Learned intents", "Execution planning"),
    "WORKFLOW_RUNTIME_SPEC.md": generate_spec("Workflow Runtime Specification", "Decomposes intents into workflows.", "Mapping high-level goals to discrete steps.", "Hardcoded scripts", "Template Instantiation", "Dynamic generation", "WorkflowCreated", "Intent", "Unmappable intent", "Created -> ... -> Stopped", "Adaptive workflows", "Scheduling"),
    "PLANNER_SPEC.md": generate_spec("Planner Specification", "Determines execution parameters and policies.", "Ordering, retries, constraints.", "Direct execution", "Policy attachment", "Advanced Graph decoration", "PlanCreated", "Workflow, Context", "Unresolvable constraints", "Created -> ... -> Stopped", "Multi-agent planning", "Execution"),
    "SCHEDULER_SPEC.md": generate_spec("Scheduler Specification", "Queue-based multitasking.", "Ready/Running/Completed queues, parallelism.", "Immediate blocking", "Async tasks", "Advanced Dependency Scheduler", "TaskScheduled, TaskStarted", "Execution Graph", "Resource starvation", "Created -> ... -> Stopped", "Distributed scheduling", "Capability logic"),
    "EXECUTION_GRAPH_SPEC.md": generate_spec("Execution Graph Specification", "DAG representation for tasks.", "Model dependencies.", "Linear list", "Simple DAG", "Dynamic conditional DAG", "GraphUpdated", "None", "Cyclic dependency", "Ephemeral", "Visual graph", "Execution logic"),
    "CAPABILITY_SPEC.md": generate_spec("Capability Specification", "Defines the executable modules.", "Metadata, sandboxing.", "Python classes", "Manifests", "Isolated Sandbox", "CapabilityRegistered", "None", "Sandboxing violation", "Discovered -> ... -> Disposed", "WASM plugins", "Orchestration"),
    "CAPABILITY_LIFECYCLE.md": generate_spec("Capability Lifecycle Specification", "State machine for capabilities.", "Ensure safe loading and unloading.", "Init -> Execute", "Stateful loading", "Hot-reloading states", "CapabilityStateChanged", "Registry", "Load failure", "Discovered -> Loaded -> Validated -> Ready -> Running -> Completed -> Disposed", "Dynamic loading", "Business logic"),
    "POLICY_ENGINE_SPEC.md": generate_spec("Policy Engine Specification", "Centralized security and permissions.", "Privacy checks, execution rules.", "Hardcoded checks", "Rule Engine", "Dynamic Auth Policies", "PolicyEvaluated", "None", "Deny-by-default lock", "Created -> ... -> Stopped", "Zero-trust model", "Execution"),
    "CONTEXT_SPEC.md": generate_spec("Context Engine Specification", "Unified situational awareness.", "Coalesce Memory, Desktop, Sensors.", "Snapshot", "Reactive Context", "Predictive Context", "ContextUpdated", "Memory, Sensors", "Data staleness", "Created -> ... -> Stopped", "Continuous visual awareness", "Planning"),
    "RESOURCE_RUNTIME_SPEC.md": generate_spec("Resource Runtime Specification", "Hardware tracking.", "CPU, RAM, GPU, Battery allocation.", "None", "Basic monitoring", "Pre-emptive scheduling constraints", "ResourceStarved", "OS metrics", "OOM", "Created -> ... -> Stopped", "Cloud offloading", "Business logic"),
    "AI_GATEWAY_SPEC.md": generate_spec("AI Gateway Specification", "Abstracts reasoning engines.", "Route between Local, Cloud, Rule engines.", "Direct API calls", "Provider Abstraction", "Cost-aware dynamic routing", "ReasoningCompleted", "Providers", "Provider outage", "Created -> ... -> Stopped", "Swarm reasoning", "Planning"),
    "JOURNAL_SPEC.md": generate_spec("Journal Specification", "Immutable Execution Journal.", "Playback, learning, debugging.", "Text logs", "SQLite records", "Event Sourcing Datastore", "JournalEntryAppended", "EventBus", "Disk full", "Created -> ... -> Stopped", "Predictive ACA", "Execution")
}

adrs = {
    "0001-event-bus.md": "# ADR 0001: Event Bus\n\nAccepted. Use deterministic event bus.",
    "0002-runtime-supervisor.md": "# ADR 0002: Runtime Supervisor\n\nAccepted. Mandatory supervision for all runtimes.",
    "0003-capability-registry.md": "# ADR 0003: Capability Registry\n\nAccepted. Isolate executable logic.",
    "0004-ai-gateway.md": "# ADR 0004: AI Gateway\n\nAccepted. Route AI requests abstractly.",
    "0005-execution-journal.md": "# ADR 0005: Execution Journal\n\nAccepted. Immutable record of all execution.",
    "0006-policy-engine.md": "# ADR 0006: Policy Engine\n\nAccepted. Centralize permissions.",
    "0007-context-engine.md": "# ADR 0007: Context Engine\n\nAccepted. Unified situational awareness.",
    "0008-execution-graph.md": "# ADR 0008: Execution Graph\n\nAccepted. DAG representation for workflows.",
    "0009-scheduler.md": "# ADR 0009: Scheduler\n\nAccepted. Multitasking queues.",
    "0010-resource-runtime.md": "# ADR 0010: Resource Runtime\n\nAccepted. Hardware capability tracking.",
    "0011-runtime-lifecycle.md": "# ADR 0011: Runtime Lifecycle\n\nAccepted. Strict state machine constraints."
}

for name, content in docs.items():
    path = os.path.join(base_dir, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

for name, content in adrs.items():
    path = os.path.join(decisions_dir, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Created all specifications and ADRs.")
