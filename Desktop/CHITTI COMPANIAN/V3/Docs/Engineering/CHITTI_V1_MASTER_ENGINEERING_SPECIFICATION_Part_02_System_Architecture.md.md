# CHITTI V1 MASTER ENGINEERING SPECIFICATION

## Part 2 --- System Architecture

**Version:** 1.0 Draft

# 1. Architectural Style

CHITTI SHALL follow an event-driven, modular runtime architecture. Every
subsystem communicates through well-defined events and contracts.

# 2. High-Level Runtime Graph

Transport → ConversationRuntime → AIRuntime → InferenceRuntime →
PlannerRuntime → WorkflowRuntime → ExecutionRuntime →
VerificationRuntime → BehaviorRuntime → ExpressionRuntime → Presentation

No runtime may bypass the owner of a responsibility.

# 3. Runtime Responsibilities

  Runtime          Primary Responsibility
  ---------------- -------------------------------------
  Transport        User input/output
  Conversation     Session, routing, entity resolution
  AI               Prompt assembly, reasoning
  Inference        Provider abstraction
  Planner          Deterministic planning
  Workflow         Workflow lifecycle
  Execution        Capability execution
  Verification     Validate execution outcomes
  Behavior         Companion behavior
  Expression       Render responses
  Memory           Persistent storage
  PackageManager   Package & capability discovery

# 4. Event Architecture

Events SHALL be immutable domain messages.

Rules: - Single publisher. - Multiple subscribers allowed. - Version
every externally consumed event. - Never mutate an event after
publication.

# 5. Runtime Lifecycle

Every runtime SHALL implement: - initialize() - start() -
stop()/shutdown() - readiness reporting

BootManager is responsible for lifecycle ordering.

# 6. Boot Sequence

1.  Infrastructure
2.  Memory
3.  PackageManager
4.  AI/Inference
5.  Conversation
6.  Planner
7.  Workflow
8.  Execution
9.  Verification
10. Behavior
11. Expression
12. Presentation

# 7. Package Architecture

Package = deployable module containing: - manifest - capabilities -
models - knowledge - presentation assets

PackageManagerRuntime is the sole authority for discovery.

# 8. Adapter Architecture

Execution SHALL never directly call platform APIs.

Execution → Adapter → Platform

Adapters include: - Win32 - Browser - Filesystem - Audio - Vision -
Network

# 9. Runtime Profiles

Profiles activate subsets of existing runtimes without changing
ownership.

Desktop is the primary production profile.

# 10. Architectural Constraints

-   No circular runtime dependencies.
-   No direct capability imports inside Planner.
-   No manual package registration after integration.
-   No production dependency on tools/.

*End of Part 2.*
