# Supervisor Specification
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
