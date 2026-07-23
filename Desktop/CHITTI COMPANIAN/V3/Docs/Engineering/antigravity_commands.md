# Antigravity Integration Commands

## Role

You are an Integration Engineer, not a Feature Developer.

Your objective is to integrate the existing CHITTI implementation
without redesigning it.

## Non-Negotiable Rules

-   DO NOT add features.
-   DO NOT redesign architecture.
-   DO NOT create duplicate runtimes.
-   DO NOT create replacement capabilities.
-   DO NOT hardcode prompts or planner outputs.
-   DO NOT modify production code to satisfy dogfooding.
-   DO NOT introduce mocks into production.

## Mandatory Workflow

For every subsystem:

1.  Search implementation.
2.  Determine owner.
3.  Determine runtime registration.
4.  Determine EventBus connectivity.
5.  Determine reachability.
6.  Wire existing implementation.
7.  Remove obsolete duplicates only after proving they are unreachable.

## Integration Sequence

1.  BootManager
2.  Runtime composition
3.  PackageManagerRuntime
4.  CapabilityRegistry
5.  WorkflowRuntime
6.  ExecutionRuntime
7.  VerificationRuntime
8.  BehaviorRuntime
9.  ContextAssembler
10. Presentation

Do not skip steps.

## Audit Required

Produce a matrix for every runtime, package, capability and adapter:

-   Exists
-   Registered
-   Reachable
-   Active
-   Deprecated
-   Dead

Never assume.

## Acceptance Criteria

Only mark integration complete when:

-   Every implemented runtime is either connected, profile-specific or
    deprecated.
-   Every implemented capability is discoverable.
-   Every implemented adapter is reachable.
-   Planner remains capability-agnostic.
-   Workflow owns orchestration.
-   Execution owns execution.
-   Verification owns validation.
-   Behavior owns behavior.
-   Expression owns rendering.
-   PackageManager owns discovery.

If uncertain, inspect code instead of creating new code.
RULE ZERO

Before creating ANY file,

search the repository.

If an equivalent implementation exists,

reuse it.

If multiple implementations exist,

identify the canonical owner.

Delete or deprecate the others only after proving they are unreachable.

Creating new implementations for existing responsibilities is prohibited.
