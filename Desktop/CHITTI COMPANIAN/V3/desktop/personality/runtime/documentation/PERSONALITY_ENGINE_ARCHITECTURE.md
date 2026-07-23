# CHITTI V2 — PERSONALITY ENGINE ARCHITECTURE

## 1. Executive Summary
The **Personality Engine & Narration Platform** (`desktop/personality/runtime/`) serves as the single canonical source of truth for personality traits, speaking styles, humor, friendliness, formality, empathy, motivation, conciseness, talkativeness, and curiosity.

---

## 2. Architecture & Pipeline
```
Capability -> LLM -> Narration Composer -> Personality Engine -> Narration Style Engine -> Voice Runtime -> SpeechTimeline -> Behavior Scheduler -> Character Runtime
```

- **Single Source of Truth:** No subsystem (Voice Runtime, Behavior Scheduler, Desktop UI) may independently invent personality.
- **Influences:**
  1. Narration Composer (text rewrites)
  2. Voice Runtime (speech rate, pause length, emphasis, intonation, expression level, voice energy)
  3. Behavior Scheduler (behavior selection preferences)
  4. Desktop UI Wording (notifications, toasts, badge wording)

---

## 3. PersonalityProfile Trait Sliders (0.0 to 1.0)
- `professional`, `friendly`, `humorous`, `empathetic`, `motivational`, `concise`, `talkative`, `curious`, `playful`, `formal`, `confident`, `patient`, `encouraging`, `supportive`, `expressive`.

---

## 4. Presets Catalog
- Professional, Friendly, Teacher, Minimal, Motivational, Developer, Productivity Coach, Story Teller, Assistant, Custom.
