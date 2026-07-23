# CHITTI V2 — VOICE PLATFORM ARCHITECTURE

## 1. Executive Summary
The **Voice Runtime & Speech Platform** (`desktop/voice/runtime/`) serves as the canonical owner of language management, voice profiles, speech styles, custom pronunciation dictionaries, TTS synthesis, speech queuing, speech sessions, speech timelines, speech events, and speech caching.

---

## 2. Platform Architecture & Separation
```
LLM -> NarrationComposer -> VoiceRuntime -> Audio + SpeechTimeline -> BehaviorScheduler
```
- **Independent Architecture:** `VoiceRuntime` is completely decoupled from `CharacterRuntime`, `PresentationRuntime`, `Desktop UIRuntime`, and `Cognitive Core V1`.
- **Interface Contract:** `CharacterRuntime` consumes ONLY `SpeechTimeline`.

---

## 3. Core Subsystems

### A. LanguageManager
Supports 12 languages + Auto Detect:
- English (`en`), Telugu (`te`), Hindi (`hi`), Tamil (`ta`), Kannada (`kn`), Malayalam (`ml`), Marathi (`mr`), Bengali (`bn`), Japanese (`ja`), German (`de`), French (`fr`), Spanish (`es`), Auto Detect (`auto`).

### B. VoiceProfileManager
Manages canonical voice profiles (`prof_female`, `friendly_female`, `prof_male`, `friendly_male`, `robot`, `narrator`, custom).

### C. SpeechStyleManager
Manages 8 speaking styles (`Friendly`, `Professional`, `Teacher`, `Motivational`, `Minimal`, `Casual`, `Story`, `Assistant`).

### D. PronunciationManager
Maintains custom pronunciation dictionary (e.g. mapping `ChatGPT` $\rightarrow$ `Chat G P T`, `GitHub` $\rightarrow$ `Git Hub`, `VS Code` $\rightarrow$ `V S Code`, `Sherpa-ONNX` $\rightarrow$ `Sherpa O N N X`, `Rajamouli` $\rightarrow$ `Raja mouli`).

### E. NarrationComposer & EmotionMarkupEngine
Normalizes punctuation and whitespace, segments text into sentences/paragraphs, and attaches provider-independent speech metadata (pauses, emphasis, rate, pitch) without generating provider-specific SSML strings.

### F. SpeechCache & SpeechQueue
- **SpeechCache:** Caches synthesized audio and `SpeechTimeline` metadata for repeated responses.
- **SpeechQueue:** Priority queue supporting `INTERRUPT`, `REPLACE`, `APPEND`, `MERGE`, and `CANCEL` operations.
