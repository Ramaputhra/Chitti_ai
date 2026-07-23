# Platform Compatibility

This document defines the ABI (Application Binary Interface) and compatibility commitments for the CHITTI architecture. These boundaries are considered frozen and must not be altered by future sprints or feature additions.

## Frozen Contracts

These contracts define the core cognitive pipeline and execution engine. They must never be bypassed or redefined.

- **`PlanningContext`**: The root abstraction for the current user turn and available capabilities.
- **`Decision`**: The pure-data output of the `DecisionEngine`.
- **`Workflow`**: The immutable execution ABI containing `Metadata`, `ExecutionPolicy`, `WorkflowSteps`, and `Version`.
- **`ExecutionPolicy`**: Per-step execution parameters (retryable, timeout_class, idempotent, priority).
- **`ExecutionContext`**: Immutable context exposing runtimes to the executing steps.
- **`ExecutionResult`**: The universal, declarative runtime output contract.
- **`Runtime Kernel API`**: The operating system layer. Runtimes must plug into the Kernel rather than modifying it. Specifically:
  ```python
  def execute(
      workflow_step: WorkflowStep,
      execution_context: ExecutionContext,
      cancellation_token: CancellationToken
  ) -> ExecutionResult:
  ```

## Stable Interfaces

These runtimes are the primary execution vehicles. They provide stable APIs that plug into the Runtime Kernel.

- **Capability Runtime**: Hardware and software integrations.
- **Memory Runtime**: Semantic, episodic, and working memory.
- **Inference Runtime**: Local LLMs, routing, and embeddings.
- **Expression Runtime**: Avatar animations, emotion sync, and TTS.

## Experimental

The following domains remain fluid and are expected to evolve dynamically as new algorithms and models are integrated:

- Memory algorithms and ranking
- Planner heuristics and decision confidence scoring
- LLM routing logic
- Avatar behaviors and micro-animations
