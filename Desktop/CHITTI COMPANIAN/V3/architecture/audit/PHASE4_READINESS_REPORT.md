# Phase 4 Readiness Report

## Overall Verdict: 🟠 Phase 4 Blocked — Major Refactoring Required

## Justification
While the core logic of Phase 0-3 is sound and beautifully adheres to the constitutional rules, the underlying **infrastructure** required to support Phase 4 (Workflow Orchestration) is not mature enough. 

Phase 4 introduces true multitasking, complex DAG generation, and stateful lifecycle tracking. If we build this on top of the current foundation, the following architectural flaws will compound:

1. **Dependency Injection Bypass:** Runtimes are currently loading their own config files and instantiating their own dependencies. This breaks Rule 2 and makes unit testing the new Workflow Runtime nearly impossible to do cleanly.
2. **Missing Cancellation Tokens:** The Workflow Runtime requires the ability to cancel executing graphs (as specified in Rule 41). The current EventBus and Runtime interfaces lack cooperative cancellation tokens.
3. **EventBus Security:** The EventBus currently allows any component to emit any event. Before Planner and Scheduler start making execution decisions, we must guarantee that `IntentRecognized` or `SpeakerVerified` was actually emitted by authorized runtimes, not by a hijacked plugin.

## Required Actions Before Phase 4
1. Refactor `ApplicationCore` to use a strict DI container (e.g., `dependency_injector` or similar pattern).
2. Refactor `IRuntime` interfaces to accept `asyncio.CancellationToken`.
3. Implement `PolicyInterceptor` inside the `BaseRuntimeSupervisor` EventBus router.

**Conclusion:** We must halt Phase 4 feature development for a short 1-2 day refactoring sprint to resolve these structural issues.
