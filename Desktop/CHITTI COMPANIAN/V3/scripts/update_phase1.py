import os
import glob
import re

base_dir = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\architecture"

new_runtime_spec = """# Base Runtime Specification
> **1. The architecture must remain deterministic by default. AI reasoning is an optional capability, never a mandatory dependency for system operation. Any feature that can be executed through deterministic logic must not require an LLM.**
>
> **2. Every runtime must be independently testable, restartable, and replaceable without requiring changes to unrelated runtimes.**
>
> **5. Every runtime, planner, scheduler, and capability must exist only to improve the AI Desktop Companion experience. Architectural complexity must always provide measurable product value.**

## 1. Purpose
Defines the base contract (`IRuntime`) and mandatory state machine that every runtime inherits.

## 2. Responsibilities
- Provide a standardized, asynchronous interface for initialization, execution, and termination.
- Maintain and expose an internal state machine indicating current operational status.
- Expose a `health_check` endpoint for supervisor monitoring.
- Declare Capability Flags (e.g., `pause`, `restart`, `hot_reload`).
- Declare Version Compatibility (e.g., `runtime_api_version: 2.0`).
- Declare Startup Priority (`CRITICAL`, `HIGH`, `NORMAL`, `LOW`).

## 3. Interfaces
- Version 1: Linear Python classes without strict state machines.
- Version 2: Standardized `IRuntime` interface containing `initialize()`, `start()`, `stop()`, and `health_check()`. Optional interface `IPausableRuntime` extending with `pause()` and `resume()`.
- Final: Immutable application runtime traits.

## 4. Events
Runtimes do not publish their own state events; the Supervisor publishes them.

## 5. Dependencies
Base interfaces only; communication occurs via EventBus or Dependency Injection.

## 6. Failure Modes
- Initialization Failure: Fails to acquire necessary resources.
- Execution Panic: Uncaught exception during main loop execution.
- Deadlock/Timeout: Fails to respond to `health_check()` within allotted window.

## 7. Lifecycle
Mandatory Strict State Machine:
`Created -> Initializing -> Ready -> Running <-> Paused -> Stopping -> Stopped -> Failed -> Restarting -> Ready`

## 8. Future Extensions
Multi-process runtime isolation.

## 9. Out of Scope
- Inter-runtime communication protocols.
- Application-level business logic.

## Acceptance Criteria

□ Purpose is defined
□ Responsibilities are complete
□ Interfaces are documented
□ Events are documented
□ Dependencies are identified
□ Failure modes are defined
□ Lifecycle is complete
□ Future extensions are identified
□ Out-of-scope boundaries are defined
□ Version 1 / Version 2 / Final Architecture comparison is complete
"""

new_supervisor_spec = """# Supervisor Specification
> **1. The architecture must remain deterministic by default. AI reasoning is an optional capability, never a mandatory dependency for system operation. Any feature that can be executed through deterministic logic must not require an LLM.**
>
> **2. Every runtime must be independently testable, restartable, and replaceable without requiring changes to unrelated runtimes.**
>
> **5. Every runtime, planner, scheduler, and capability must exist only to improve the AI Desktop Companion experience. Architectural complexity must always provide measurable product value.**

## 1. Purpose
Defines the Runtime Supervisor, a deterministic watchdog managing the lifecycle, health, and fault tolerance of individual runtimes.

## 2. Responsibilities
- Instantiate, start, and stop the supervised `IRuntime`.
- Monitor health via Heartbeats, active checks, and timeout detection.
- Enforce Restart Policies based on runtime Capability Flags.
- Publish deterministic lifecycle events to the EventBus.

## 3. Interfaces
- Version 1: None (Kernel managed runtimes directly).
- Version 2: `IRuntimeSupervisor` wrapping an `IRuntime`.
- Final: Cluster-aware distributed supervision.

## 4. Events
- `RuntimeStateChanged`
- `RuntimeFaultDetected`
- `RuntimeRestartAttempted`

## 5. Dependencies
EventBus, `IRuntime` interface.

## 6. Failure Modes
- Recovery Exhaustion: Max retries reached; escalated to Core.
- Supervisor Panic: Fatal supervisor crash.

## 7. Lifecycle
`Created -> Supervising -> Recovering -> Terminated -> Escalated`

## 8. Future Extensions
Circuit breaker patterns.

## 9. Out of Scope
Domain logic execution.

## Acceptance Criteria

□ Purpose is defined
□ Responsibilities are complete
□ Interfaces are documented
□ Events are documented
□ Dependencies are identified
□ Failure modes are defined
□ Lifecycle is complete
□ Future extensions are identified
□ Out-of-scope boundaries are defined
□ Version 1 / Version 2 / Final Architecture comparison is complete
"""

new_core_spec = """# Application Core Specification
> **1. The architecture must remain deterministic by default. AI reasoning is an optional capability, never a mandatory dependency for system operation. Any feature that can be executed through deterministic logic must not require an LLM.**
>
> **2. Every runtime must be independently testable, restartable, and replaceable without requiring changes to unrelated runtimes.**
>
> **5. Every runtime, planner, scheduler, and capability must exist only to improve the AI Desktop Companion experience. Architectural complexity must always provide measurable product value.**

## 1. Purpose
Defines the Application Core, the central orchestrator managing startup/shutdown sequencing and global services.

## 2. Responsibilities
- Runtime Registration: Maintain a registry of available supervisors/runtimes.
- Dependency Resolver: A dedicated component to dynamically resolve and sort runtime dependencies (DAG).
- Startup Sequencing: Execute Boot Sequence based on sorted DAG and Runtime Priorities.
- Shutdown Sequencing: Gracefully teardown supervisors.
- Global Error Handling: Catch escalated failures.

## 3. Interfaces
- Version 1: Linear procedural startup.
- Version 2: `ApplicationCore` managing `IRuntimeSupervisor` instances, a `DependencyResolver`, and the `EventBus`.
- Final: Declarative containerized core.

## 4. Events
- `ApplicationCoreStarting`
- `ApplicationCoreReady`
- `ApplicationCoreShuttingDown`
- `ApplicationCorePanic`

## 5. Dependencies
EventBus, Configuration manager.

## 6. Failure Modes
- Dependency Cycle Detected: Application refuses to boot.
- Core Service Failure: Critical runtime failure causes panic.

## 7. Lifecycle
`Booting -> Validating -> StartingSupervisors -> Running -> StoppingSupervisors -> Terminated`

## 8. Future Extensions
Dynamically loading plugins.

## 9. Out of Scope
Routing user intents.

## Acceptance Criteria

□ Purpose is defined
□ Responsibilities are complete
□ Interfaces are documented
□ Events are documented
□ Dependencies are identified
□ Failure modes are defined
□ Lifecycle is complete
□ Future extensions are identified
□ Out-of-scope boundaries are defined
□ Version 1 / Version 2 / Final Architecture comparison is complete
"""

with open(os.path.join(base_dir, "RUNTIME_SPEC.md"), "w", encoding='utf-8') as f:
    f.write(new_runtime_spec)
with open(os.path.join(base_dir, "SUPERVISOR_SPEC.md"), "w", encoding='utf-8') as f:
    f.write(new_supervisor_spec)
with open(os.path.join(base_dir, "APPLICATION_CORE_SPEC.md"), "w", encoding='utf-8') as f:
    f.write(new_core_spec)

print("Updated Phase 1 specifications.")
