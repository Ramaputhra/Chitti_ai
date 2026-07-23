import os

base_dir = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\architecture"

golden_rules = """> **1. The architecture must remain deterministic by default. AI reasoning is an optional capability, never a mandatory dependency for system operation. Any feature that can be executed through deterministic logic must not require an LLM.**
>
> **2. Every runtime must be independently testable, restartable, and replaceable without requiring changes to unrelated runtimes.**
>
> **5. Every runtime, planner, scheduler, and capability must exist only to improve the AI Desktop Companion experience. Architectural complexity must always provide measurable product value.**
"""

acceptance_criteria = """## Acceptance Criteria

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
"""

specs = {
    "CHARACTER_RUNTIME_SPEC.md": f"""# Character Runtime Specification
{golden_rules}
## 1. Purpose
Defines CHITTI's personality, speaking style, and behavioral quirks. It guarantees the companion feels alive and consistent without requiring LLM inference for standard responses.

## 2. Responsibilities
- Provide a **100% deterministic** response selection from curated JSON datasets based on intent or state.
- Apply personality constraints (e.g., formal vs. casual, humor, catchphrases).
- Adapt behavior based on the loaded user profile (e.g., addressing the user as "Boss" vs. "Sir").

## 3. Interfaces
- Subscribes to: `IntentRecognized`, `TaskStarted`, `TaskCompleted`.
- Emits: `CharacterResponseSelected`.
- API: Implement `IRuntime`.

## 4. Events
- `CharacterResponseSelected`

## 5. Dependencies
- EventBus
- User Profile / Settings (for personality preferences)

## 6. Failure Modes
- Missing dataset mapping defaults to a safe generic response.

## 7. Lifecycle
Follows standard `IRuntime` strict state machine (`CREATED` -> `INITIALIZING` -> `READY` -> `RUNNING`).

## 8. Future Extensions
- Dynamic voice cloning style adjustments.

## 9. Out of Scope
- **Strictly NO LLM.** The runtime relies entirely on weighted randomization over predefined text arrays.

{acceptance_criteria}""",

    "EMOTION_RUNTIME_SPEC.md": f"""# Emotion Runtime Specification
{golden_rules}
## 1. Purpose
Maintains CHITTI's internal emotional state machine based purely on systemic events rather than abstract language analysis.

## 2. Responsibilities
- Act as a **100% deterministic** state machine mapping system events to emotional states (e.g., Happy, Curious, Thinking, Concerned, Relaxed).
- Prevent emotional thrashing (e.g., debouncing rapid state changes).
- Maintain an emotional baseline based on recent task success/failure ratios.

## 3. Interfaces
- Subscribes to: `TaskStarted` (-> Thinking), `TaskFinished` (-> Happy), `TaskFailed` (-> Concerned), `IdleTimeout` (-> Relaxed).
- Emits: `EmotionStateChanged`.
- API: Implement `IRuntime`.

## 4. Events
- `EmotionStateChanged`

## 5. Dependencies
- EventBus

## 6. Failure Modes
- Invalid event sequence handled by ignoring or defaulting to Idle/Relaxed.

## 7. Lifecycle
Follows standard `IRuntime` strict state machine (`CREATED` -> `INITIALIZING` -> `READY` -> `RUNNING`).

## 8. Future Extensions
- Advanced mood decaying over days.

## 9. Out of Scope
- **Strictly NO LLM.** Emotion is an explicit derivation of execution context and conversation state, never randomly generated or guessed by an AI.

{acceptance_criteria}""",

    "EXPRESSION_RUNTIME_SPEC.md": f"""# Expression Runtime Specification
{golden_rules}
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

{acceptance_criteria}""",

    "NARRATION_RUNTIME_SPEC.md": f"""# Narration Runtime Specification
{golden_rules}
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

{acceptance_criteria}"""
}

for filename, content in specs.items():
    path = os.path.join(base_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        
print("Behavior Runtimes specs generated successfully.")
