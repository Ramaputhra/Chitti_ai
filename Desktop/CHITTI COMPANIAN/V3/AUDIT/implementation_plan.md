# Phase 5.5: Present (Experience 001 Completion)

## Goal Description
Implement the **Present** phase of Experience 001 by introducing the **Presentation Runtime** and **Presence Engine**. 

> [!IMPORTANT]
> **Presentation communicates verified truth. It never determines truth.** Verification decides success; Presentation decides how that success is communicated.

The Presentation layer owns:
- Avatar behavior (Animations, Idle presence)
- Speech (Piper TTS)
- Follow-up window & Edge-docked mode
- Resident mode transitions & User attention management

## Proposed Changes

---

### 1. Constitutional Updates
#### [MODIFY] [AGENTS.md](file:///c:/Users/Sm!le/Desktop/CHITTI%20COMPANIAN/V3/.agents/AGENTS.md)
Append the Presentation Constitution:
- **Rule 40**: Presentation never determines truth. Verification determines truth. Presentation determines how verified truth reaches the user.
- **Rule 41**: Speech exists only when it adds information beyond what the user can already perceive.
- **Rule 42**: Avatar is the primary communication channel. Animation > Sound > Speech.
- **Rule 43**: Minimized is not inactive. Edge-docked CHITTI remains fully alive.

---

### 2. Presentation Models
#### [NEW] [presentation_models.py](file:///c:/Users/Sm!le/Desktop/CHITTI%20COMPANIAN/V3/desktop/models/presentation_models.py)
- **`PresentationPriority`**: Enum (HIGH, NORMAL, LOW)
- **`PresentationPolicy`**: Declarative structure (voice, avatar_animation, sound_effect, toast, followup_window, allow_interrupt, priority).
- **`PresentationDecision`**: Built decision containing response_text, language, voice, avatar_animation, etc.
- **`PresenceState`**: Enum (ACTIVE, FOLLOW_UP_WINDOW, TASK_EXECUTION, EDGE_DOCKED_WORKING, EDGE_DOCKED_IDLE, RELAXED_IDLE, GOODBYE, RESIDENT_MODE).
- **Events**: `PresentationStarted`, `PresentationCompleted`, `PresenceStateChanged`, `ResponseCreatedEvent`.

---

### 3. Response Builder
#### [NEW] [response_builder.py](file:///c:/Users/Sm!le/Desktop/CHITTI%20COMPANIAN/V3/desktop/platform/core/response_builder.py)
- Converts verified results into communication (e.g., `Response(text="Compression completed.", importance=NORMAL)`). The Presentation Runtime never builds sentences.

---

### 4. Presentation & Presence Runtimes
#### [NEW] [presentation_runtime.py](file:///c:/Users/Sm!le/Desktop/CHITTI%20COMPANIAN/V3/desktop/platform/core/presentation_runtime.py)
- Subscribes strictly to `VERIFICATION_COMPLETED`, `WORKFLOW_FAILED`, `SYSTEM_NOTIFICATION`.
- Applies the Presentation Constitution to determine speech vs animation. Manages the Response Builder and invokes the Presence Engine.

#### [NEW] [presence_runtime.py](file:///c:/Users/Sm!le/Desktop/CHITTI%20COMPANIAN/V3/desktop/platform/core/presence_runtime.py)
- Implements the entire lifecycle state machine (`ACTIVE` -> `FOLLOW_UP_WINDOW` -> `EDGE_DOCKED_IDLE` -> `RELAXED_IDLE` -> `GOODBYE` -> `RESIDENT_MODE`).

---

### 5. Expression Adapter & Kernel
#### [NEW] [expression_adapter.py](file:///c:/Users/Sm!le/Desktop/CHITTI%20COMPANIAN/V3/desktop/platform/components/adapters/expression_adapter.py)
- Bridge to Piper (TTS) and the Avatar. No business logic.

#### [MODIFY] [runtime_kernel.py](file:///c:/Users/Sm!le/Desktop/CHITTI%20COMPANIAN/V3/desktop/platform/core/runtime_kernel.py)
- Routes `WORKFLOW_COMPLETED` to `PresentationRuntime` and `PresenceRuntime`. The Kernel never directly manipulates UI.

---

## Verification Plan

`test_presentation_runtime.py` will validate:
1. **Open Downloads (Silent)**: Joy animation + Follow-up window. No speech.
2. **Task Execution**: Working animation -> Progress speech -> Completion speech -> Follow-up.
3. **Minimize**: State shifts to `EDGE_DOCKED_WORKING`. Wake word expands avatar. Task continues.
4. **Idle Lifecycle**: 20s (Edge dot) -> 1 min (Yoga) -> 2 mins (Goodbye) -> Resident Mode.
5. **Interrupt**: User speaks -> Speech stops immediately -> Listening resumes.
