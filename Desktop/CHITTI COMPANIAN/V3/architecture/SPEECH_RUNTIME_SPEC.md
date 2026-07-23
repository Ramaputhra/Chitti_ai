# Speech Runtime Specification
> **1. The architecture must remain deterministic by default. AI reasoning is an optional capability, never a mandatory dependency for system operation. Any feature that can be executed through deterministic logic must not require an LLM.**
>
> **2. Every runtime must be independently testable, restartable, and replaceable without requiring changes to unrelated runtimes.**
>
> **5. Every runtime, planner, scheduler, and capability must exist only to improve the AI Desktop Companion experience. Architectural complexity must always provide measurable product value.**

## 1. Purpose
Handles the intake of microphone audio, detects human speech, identifies the spoken language, transcribes it into text using language-specific STT providers, and broadcasts a standardized text envelope.

## 2. Responsibilities
- **Provider Interface:** Manage an interchangeable suite of STT providers (e.g., `EnglishSTTProvider`, `IndicConformerProvider`).
- **Language Detection:** Dynamically detect the spoken language to route audio to the optimal primary or multi-lingual STT provider.
- **Normalization:** Ensure that everything downstream receives exactly the same normalized format: `text`, `language`, and `confidence`. 
- Completely encapsulate all STT and VAD logic so that Intent, Workflow, and Planner runtimes are completely STT-independent.

## 3. Interfaces
- **Inputs:** Microphone Audio Stream, Wake Word trigger, Optional Voice Authentication (ECAPA-TDNN), Silero VAD.
- **Outputs:** Emits `SpeakerVerified` and `SpeechTranscribed` events.
- **Note:** The pipeline continues to generate `SpeechTranscribed` events regardless of the `SpeakerVerified` outcome. Authentication is handled by the Policy Engine.
- **API:** Implement `IRuntime`.

## 4. Events
- `SpeakerVerified`
  ```yaml
  speaker_id: "user_123"
  confidence: 0.95
  authenticated: true
  ```
- `SpeechTranscribed`
  ```yaml
  text: "బ్రౌజర్ ఓపెన్ చేయ్"
  language: "te"
  confidence: 0.98
  ```

## 5. Dependencies
- EventBus
- Local Microphone Access
- Local STT Providers (e.g., Whisper, IndicConformer)
- Local Speaker Verification Model (ECAPA-TDNN)

## 6. Failure Modes
- If primary language detection fails, fallback to default (English) STT.
- If confidence is extremely low, optionally retry with a secondary multi-lingual fallback.

## 7. Lifecycle
Follows standard `IRuntime` strict state machine (`CREATED` -> `INITIALIZING` -> `READY` -> `RUNNING`). Must manage internal heavy ML model loading carefully during `INITIALIZING`.

## 8. Future Extensions
- Dynamic multi-speaker diarization.
- Handling "Tenglish" mixed-language speech through specialized cross-lingual providers.

## 9. Out of Scope
- The Speech Runtime **never** attempts to understand meaning, extract intents, or execute workflows. It strictly performs Speech-To-Text.

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
