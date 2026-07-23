# Application Core Specification
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
