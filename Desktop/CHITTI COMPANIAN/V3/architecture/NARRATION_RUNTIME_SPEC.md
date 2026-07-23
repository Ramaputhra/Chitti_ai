# Narration Runtime Specification
> **1. The architecture must remain deterministic by default. AI reasoning is an optional capability, never a mandatory dependency for system operation. Any feature that can be executed through deterministic logic must not require an LLM.**
>
> **2. Every runtime must be independently testable, restartable, and replaceable without requiring changes to unrelated runtimes.**
>
> **5. Every runtime, planner, scheduler, and capability must exist only to improve the AI Desktop Companion experience. Architectural complexity must always provide measurable product value.**

## 1. Purpose
Decides *when* and *what* CHITTI should speak during execution to maintain transparency and progress communication without overwhelming the user.

## 2. Responsibilities
- Track active workflows and emit progress updates (e.g., "Downloading...", "Extracting...").
- Suppress micro-updates to prevent verbal spam.
- **Dual-Mode Operation:**
  - *Deterministic Mode (Default):* Uses template engine for discrete tasks (e.g., `Task=Open Browser -> "Opening browser."`).
  - *AI Mode (Optional Fallback):* When a complex macro-workflow completes, passes the execution log to the LLM to generate a natural, concise summary (e.g., "I've downloaded, organized, and uploaded your files.").

## 3. Interfaces
- Subscribes to: `WorkflowProgressed`, `WorkflowCompleted`.
- Emits: `NarrationPrepared` (to be stylized by CharacterRuntime).
- API: Implement `IRuntime`.

## 4. Events
- `NarrationPrepared`

## 5. Dependencies
- EventBus
- AI Gateway (only for AI mode fallback)

## 6. Failure Modes
- LLM generation failure falls back immediately to deterministic template summary.

## 7. Lifecycle
Follows standard `IRuntime` strict state machine (`CREATED` -> `INITIALIZING` -> `READY` -> `RUNNING`).

## 8. Future Extensions
- Adaptive verbosity based on user's current cognitive load.

## 9. Out of Scope
- **Hybrid Rule.** Defaults to deterministic templates (0 LLM overhead). Only escalates to LLM inference when the workflow complexity exceeds standard template capability. It does NOT generate raw UI or execute capabilities.

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
