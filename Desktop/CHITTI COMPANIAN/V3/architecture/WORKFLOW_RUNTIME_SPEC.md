# Workflow Runtime Specification

> **1. The architecture must remain deterministic by default.**
>
> **2. Every runtime must be independently testable, restartable, and replaceable.**
>
> **Rule 240 – Orchestration Boundaries:** Workflow describes what should happen. Planner determines how it should be prepared. Execution Graph describes task dependencies.
>
> **Rule 241 – Workflow Instance Immutability:** Workflow Templates are immutable definitions. Workflow Instances are mutable runtime objects. Planner, Scheduler, and Execution Runtime must operate only on Workflow Instances.

## 1. Purpose
Converts a verified `IntentRecognized` event into a mutable `WorkflowInstance` instantiated from an immutable `WorkflowTemplate`. It tracks the lifecycle of the instance and publishes progress events.

## 2. Responsibilities
- **Template Resolution:** Loads immutable JSON-backed deterministic templates (e.g., `desktop/config/workflows/OPEN_APPLICATION.json`).
- **Instance Creation:** Generates a globally unique `instance_id` (e.g., `WF-00001238`) and instantiates a `WorkflowInstance`.
- **Context Injection:** Injects `WorkflowContext` (conversation_id, speaker_id, language, desktop_session, priority) into the instance so downstream runtimes don't have to query for it.
- **Lifecycle Management:** Tracks the state of the instance: `CREATED` -> `VALIDATED` -> `PLANNED` -> `GRAPH_CREATED` -> `SCHEDULED` -> `RUNNING` -> `COMPLETED` / `FAILED` / `CANCELLED`.
- **Cancellation:** Supports canceling a workflow cleanly by updating its lifecycle state, instead of hard-killing processes.
- **LLM Fallback (Synthesis):** If a deterministic template is missing, delegates to the `AIGateway` to synthesize a logical workflow definition.

## 3. Interfaces
- **Inputs:** `IntentRecognized` (from Intent Runtime), `WorkflowStatusUpdate` (from downstream runtimes).
- **Outputs:** Emits lifecycle progress events.
- **API:** Implement `IRuntime`.

## 4. Events
- `WorkflowCreated`
- `WorkflowValidated`
- `WorkflowCancelled`
- `WorkflowFailed`
- `WorkflowCompleted`

Each event carries the `WorkflowInstance`, allowing the Character Runtime to say things like "Chrome is opening..." without polling.

## 5. Dependencies
- EventBus
- Local Workflow Template Registry
- AI Gateway

## 6. Out of Scope
- **Execution Graphs:** Never constructs Directed Acyclic Graphs.
- **Planner Enrichment:** Does not assign capabilities or policies.

## Acceptance Criteria
□ Instance vs Template separation
□ Context propagation
□ Unique non-reusable IDs
□ Lifecycle states and transitions
□ Cancellation logic
