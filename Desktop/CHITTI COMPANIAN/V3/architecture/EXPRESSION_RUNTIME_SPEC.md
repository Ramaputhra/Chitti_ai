# Expression Runtime Specification
> **1. The architecture must remain deterministic by default. AI reasoning is an optional capability, never a mandatory dependency for system operation. Any feature that can be executed through deterministic logic must not require an LLM.**
>
> **2. Every runtime must be independently testable, restartable, and replaceable without requiring changes to unrelated runtimes.**
>
> **5. Every runtime, planner, scheduler, and capability must exist only to improve the AI Desktop Companion experience. Architectural complexity must always provide measurable product value.**

## 1. Purpose
Acts as the physical and visual driver, translating abstract emotional states into concrete hardware and UI commands.

## 2. Responsibilities
- Provide a **100% deterministic** mapping from `EmotionState` to output modalities.
- Map emotions to specific Eye and Mouth animations.
- Map emotions to servo movements (e.g., nodding, looking down).
- Adjust voice prosody parameters (e.g., pitch, speed) for the Speech Runtime.

## 3. Interfaces
- Subscribes to: `EmotionStateChanged`, `CharacterResponseSelected`.
- Emits: `ExpressionCommandIssued` (Consumed by Avatar/Hardware Runtimes).
- API: Implement `IRuntime`.

## 4. Events
- `ExpressionCommandIssued`

## 5. Dependencies
- EventBus
- Emotion Runtime (via Events)

## 6. Failure Modes
- Hardware disconnect leads to UI-only fallback.

## 7. Lifecycle
Follows standard `IRuntime` strict state machine (`CREATED` -> `INITIALIZING` -> `READY` -> `RUNNING`).

## 8. Future Extensions
- Synchronizing expressions with audio waveforms (lipsync).

## 9. Out of Scope
- **Strictly NO LLM.** Pure mapping matrix (e.g., `Emotion=Happy -> Eyes=Smile, Mouth=Smile, Servo=Nod`).

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
