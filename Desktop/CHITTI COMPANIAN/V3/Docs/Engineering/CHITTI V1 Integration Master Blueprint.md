# CHITTI V1 Integration Master Blueprint

## Mission

Freeze feature development. Complete V1 by integrating existing
subsystems into one production execution graph.

## Engineering Principles

-   Integration before implementation.
-   Search before creating.
-   Never duplicate an existing runtime, package, adapter, capability or
    model.
-   Preserve deterministic execution boundaries.
-   LLM is for reasoning, dialogue and semantic understanding---not
    authority over deterministic execution.
-   Product runtime remains the source of truth. Test tools must never
    alter production architecture.

# Current Audit Summary

  Domain                Status
  --------------------- ------------
  Architecture          Excellent
  Package System        Excellent
  Memory                Excellent
  Execution             Excellent
  Infrastructure        Excellent
  Runtime Integration   Incomplete

Primary problem: **Existing subsystems are implemented but not fully
connected.**

# Target Runtime Graph

Transport → Conversation → AI → Inference → Planner → Workflow →
Execution → Verification → Behavior → Expression → Presentation

# Target Memory Graph

Conversation → MemoryRuntime → SQLite → Activity → Execution History →
ContextAssembler → AIRuntime → Prompt

# Integration Order

1.  BootManager & Runtime Composition
2.  PackageManagerRuntime
3.  Capability Discovery
4.  WorkflowRuntime
5.  ExecutionRuntime
6.  VerificationRuntime
7.  BehaviorRuntime
8.  ContextAssembler
9.  Adapter Layer
10. Presentation

Each stage must be completed before proceeding.

# Runtime Ownership

ConversationRuntime: - session lifecycle - entity resolution -
conversation routing

AIRuntime: - prompt assembly - semantic reasoning

PlannerRuntime: - deterministic planning only

WorkflowRuntime: - workflow lifecycle

ExecutionRuntime: - capability execution

VerificationRuntime: - validate outcomes using observers/adapters

BehaviorRuntime: - behavioral events

ExpressionRuntime: - user-facing output

# Package Rules

PackageManagerRuntime becomes sole authority for: - package discovery -
dependency resolution - capability registration

No manual registry.register() once parity is achieved.

# Memory Rules

ConversationSession = RAM

SQLite = persistent history

Never serialize runtime session objects directly.

# Cleanup Rules

Delete code only after proving: - no imports - no runtime composition -
no EventBus references - no package references - no planner/workflow
references

Otherwise classify as: - Active - Profile-specific - Deprecated

# V1 Exit Criteria

-   Every runtime classified.
-   Every capability classified.
-   Every adapter classified.
-   Zero duplicate active implementations.
-   Zero manual capability registration.
-   Full execution graph connected.
-   Verification feedback connected.
-   ContextAssembler injects all required context.
-   No feature work until integration complete.
