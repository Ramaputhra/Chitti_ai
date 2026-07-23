# Execution Graph Runtime Specification

> **1. The architecture must remain deterministic by default. AI reasoning is an optional capability, never a mandatory dependency for system operation. Any feature that can be executed through deterministic logic must not require an LLM.**

## 1. Purpose
Converts a Planner-enriched workflow into an immutable Directed Acyclic Graph (DAG) explicitly defining task dependencies to enable safe, parallel execution by the Scheduler. 

## 2. Responsibilities
- **Graph Construction:** Parses the enriched workflow and constructs a formal DAG structure.
- **Exclusive Generator Rule:** ExecutionGraph is generated exclusively by the Execution Graph Runtime. No other runtime may create or mutate execution graphs.
- **Node Metadata Extraction:** Wraps each logical step into a heavily typed Node carrying metadata required for scheduling:
  ```yaml
  node_id: "launch_browser"
  capability: "OpenApplication"
  inputs:
    app: "chrome.exe"
  timeout: 30
  retry: 2
  parallel: false
  ```
- **Graph Validation:** Validates the constructed graph before publishing:
  - Cycle detection (prevents infinite dependency loops).
  - Detects orphan nodes (no parents and not a root).
  - Detects duplicate Node IDs.
  - Detects missing dependencies.
  - Detects invalid capability references.
  - Detects unreachable nodes.
- **Immutability Guarantee:** Emits a completely immutable `ExecutionGraphReady` event. If the Planner needs to modify the plan later, a new graph must be generated.

## 3. Interfaces
- **Inputs:** `PlannerEnrichedWorkflow` (From Planner Runtime).
- **Outputs:** Emits `ExecutionGraphReady` or `GraphValidationFailed`.
- **API:** Implement `IRuntime`.

## 4. Events
- `ExecutionGraphReady`
- `GraphValidationFailed`

## 5. Dependencies
- EventBus

## 6. Out of Scope
- **Policy Enforcement:** Does not decide *what* capabilities are needed; assumes the Planner has already done so.
- **Workflow Decomposition:** Does not figure out what steps are required; assumes Workflow Runtime and Planner have done so.
- **Execution:** Never actually executes the graph or allocates threads.

## Acceptance Criteria
□ Purpose is defined
□ Exclusive Generator Rule documented
□ Graph Validation metrics identified
□ Out-of-scope boundaries are defined
