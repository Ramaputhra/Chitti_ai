# CHITTI V2 — BEHAVIOR SCRIPT SPECIFICATION

## 1. Executive Summary
This specification defines the declarative **BehaviorScript** model and the event-driven orchestration architecture of CHITTI V2 (`desktop/character/behavior/`).

`BehaviorScript` is the primary, declarative output produced by `BehaviorScheduler`. It describes character behavior intentions, trigger conditions, and loop rules without hardcoding playback timestamps.

---

## 2. BehaviorScript Structure
```python
@dataclass
class BehaviorScript:
    script_id: str
    session_id: str
    intent_name: str
    instructions: List[ScriptInstruction]
```

### ScriptInstruction:
- `behavior_id`: Permanent behavior ID (`CHR_TALK_EXPLAIN_001`, `CHR_GEST_POINT_SCR_001`, etc.)
- `behavior_name`: Human-readable behavior name (`TalkingExplain`, `PointScreen`, etc.)
- `trigger_condition`: Optional event condition triggering this step (`SentenceBoundary`, `SpeechCompleted`, `ExecutionCompleted`).
- `loop_condition`: Optional condition dictating step repetition (`LoopUntilSpeechEnds`, `LoopUntilExecutionCompletes`, `LoopForever`, `LoopUntilEvent`, `LoopFixedCount`).
- `priority`: Priority level (`LOW`, `NORMAL`, `HIGH`, `CRITICAL`).
- `interruptible`: Boolean flag allowing barge-in interrupts.

---

## 3. Supported Conditions

### A. Trigger Conditions
- `WakewordDetected`
- `SpeechStarted`
- `SpeechCompleted`
- `SentenceBoundary(index)`
- `PhraseBoundary(index)`
- `Pause(duration)`
- `ExecutionStarted`
- `ExecutionCompleted`
- `ReminderTriggered`
- `ReminderCompleted`
- `PresentationStarted`
- `PresentationCompleted`
- `NavigationStarted`
- `NavigationCompleted`
- `VisionStarted`
- `VisionCompleted`
- `BrowserOpened`
- `BrowserClosed`

### B. Loop Conditions
- `LoopUntilSpeechEnds`: Loops step dynamically until TTS speech audio finishes.
- `LoopUntilExecutionCompletes`: Loops step until background workflow completes.
- `LoopForever`: Continuous resting or idle loop.
- `LoopUntilEvent`: Loops until a specific event triggers.
- `LoopFixedCount`: Loops for a fixed iteration count ($N$).

---

## 4. Canonical SpeechTimeline Interface
`SpeechTimeline` acts as the rich, single canonical interface between TTS engines and the `BehaviorScheduler`:
- `speech_id`, `audio_id`, `total_duration`, `speech_rate`, `language`, `voice`, `start_time`, `estimated_end_time`, `sentence_boundaries`, `phrase_boundaries`, `pause_points`, `emphasis_points`, `tts_provider`, `metadata`.
- *Note: SpeechTimeline contains ZERO phoneme or lip-sync timing.*

---

## 5. Behavior Timeline Compiler
`BehaviorTimelineCompiler` converts a declarative `BehaviorScript` and optional `SpeechContext` into a concrete `BehaviorTimeline`:
```
BehaviorScript + SpeechContext -> BehaviorTimelineCompiler -> BehaviorTimeline
```
Only the `CharacterRuntime` consumes compiled `BehaviorTimeline` objects for playback.
