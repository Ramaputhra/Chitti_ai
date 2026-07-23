# RG02 RELEASE DECISION MATRIX

## FINAL ENGINEERING DECISION

> Every conclusion backed by repository evidence. See `RG02_ROOT_CAUSE_DOSSIERS.md` and `RG02_DEPENDENCY_GRAPHS.md` for proof.

---

## MATRIX

| # | Component | File | Current Status | Used In Production | Dependency Count | Reverse Deps | Risk Level | Blocks Release | Safe To Modify | Safe To Delete | Canonical Owner | Minimum Safe Repair |
|---|-----------|------|---------------|-------------------|-----------------|-------------|-----------|---------------|---------------|---------------|-----------------|---------------------|
| 1 | `DeterministicPlannerStrategy` | `platform/strategies/deterministic_planner.py` | Development Shortcut (by design, confirmed `kernel.py:183`) | YES | 2 (kernel.py, test files) | 1 (PlannerRuntime) | LOW | YES (partial) | YES | NO | Canonical (temporary) | Implement `LLMPlannerStrategy`, swap in `kernel.py:185` |
| 2 | `LiteOCRProvider` | `platform/providers/ocr/liteocr_provider.py` | Mock (hardcoded output) | NO | 1 (verify script only) | 0 (production) | LOW | NO | YES | NO (needs audit) | Not canonical path | Implement real ONNX inference, register capability |
| 3 | `LaunchApplicationCapability` (legacy) | `packages/desktop_pack/capabilities/application.py` | Dead Code (superseded by `execution.py`) | NO | 0 | 0 | SAFE | NO | YES | NOT YET SAFE (Rule: 7 criteria not all proven) | Add deprecation marker, confirm no dynamic load, then delete |
| 4 | `LaunchApplicationCapability` (canonical) | `packages/desktop_pack/capabilities/execution.py` | Production Ready | YES | 1 (CapabilityProvider) | 1 (WorkflowRuntime) | LOW | NO | YES | NO | Canonical | No repair needed |
| 5 | `PyAutoGUIEngine` | `runtimes/environment/adapters/desktop/engine.py` | Stub (prints, returns True) | NO | 1 (selector.py) | 0 (production) | LOW | NO | YES | NO | Canonical interface | Implement Win32/PyAutoGUI OS calls |
| 6 | `PlaywrightEngine` | `runtimes/environment/adapters/browser/engine.py` | Stub (prints, returns True) | NO | 1 (adapter.py) | 0 (production) | LOW | NO | YES | NO | Canonical interface | Implement Playwright automation |
| 7 | `DesktopActivityRuntime` | `runtimes/activity/desktop_activity_runtime.py` | Production Ready (broken wiring) | NO (not in boot) | 0 (production) | 0 (production) | LOW | NO | YES | NO | Canonical (analytics) | Add to `compose_runtimes()`, add async polling loop in `start()` |
| 8 | `MockLLMProvider` (inference) | `platform/inference/inference/mock_llm.py` | Test Helper | NO | 0 (production) | 2 (test files) | SAFE | NO | YES | NO (test dependency) | Test only — no repair needed |
| 9 | `MockLLMProvider` (services) | `services/language/providers/mock_llm.py` | Test Helper | NO | 0 | 0 | SAFE | NO | YES | NO (needs audit) | Test only — no repair needed |
| 10 | `MockWakeWordProvider` | `services/audio/providers/mock_wake_word.py` | Test Helper | NO | 0 | 0 | SAFE | NO | YES | NO (needs audit) | Test only — no repair needed |
| 11 | `MockSpeechProvider` | `services/language/providers/mock_speech.py` | Test Helper | NO | 0 | 0 | SAFE | NO | YES | NO (needs audit) | Test only — no repair needed |
| 12 | `IEmotionRuntime` | `behavior/emotion_runtime.py` | Architecture Blueprint (ABC only) | NO | 0 | 0 | SAFE | NO | YES | NO | Not Canonical (no implementation) | Future implementation sprint |
| 13 | `OpenWakeWordProvider` | `services/audio/providers/open_wake_word_provider.py` | Production Ready (package-dependent) | YES | 1 (VoiceTransport) | 0 | MEDIUM | YES (if package missing) | YES | NO | Canonical | Ensure `openwakeword` + ONNX in requirements |
| 14 | `FasterWhisperProvider` | `services/audio/providers/faster_whisper_provider.py` | Production Ready (package-dependent) | YES | 1 (VoiceTransport) | 0 | MEDIUM | YES (if package missing) | YES | NO | Canonical | Ensure `faster_whisper` in requirements; verify `process_audio_stream` streaming stub |
| 15 | `PiperProvider` | `services/audio/providers/piper_provider.py` | Production Ready (model-dependent) | YES | 1 (VoiceTransport) | 0 | MEDIUM | YES (if model missing) | YES | NO | Canonical | Ensure voice model exists at expected path |
| 16 | `GGUFInferenceProvider` | `platform/inference/inference/gguf_provider.py` | Production Ready (model-dependent) | YES (use_llm=True) | 1 (kernel.py) | 1 (InferenceRuntime) | MEDIUM | YES (if model missing) | YES | NO | Canonical | Ensure `qwen2.5-1.5b-instruct-q4_k_m.gguf` exists; verify `llama_cpp` installed |
| 17 | `ExpressionRuntime` | `runtimes/expression_runtime.py` | Production Ready | YES | 1 (compose_runtimes) | 0 | LOW | NO | YES | NO | Canonical | No repair needed |
| 18 | `DistanceCapability` (not registered) | `packages/desktop_pack/capabilities/distance.py` | Not Registered (broken wiring) | NO | 0 | 1 (DeterministicPlannerStrategy references it) | MEDIUM | YES | YES | NO | Unknown | Register in `CapabilityProvider` or remove from planner routing |
| 19 | `FasterWhisperProvider.process_audio_stream` | line 107–121 | Hardcoded stub | YES (called during stream) | 1 (FasterWhisperProvider) | 0 | LOW | NO (streaming only) | YES | NO | Canonical | Remove hardcoded `"Hello Chitti"` stream yielding; implement real `faster_whisper` stream |

---

## ANSWERS TO FINAL ENGINEERING QUESTIONS

---

### Q1. Which blockers are REAL?

**Real release blockers (proven by production wiring evidence):**

#### BLOCKER R1 — DeterministicPlannerStrategy: DistanceCapability / ResumeActivityCapability routing mismatch
**Evidence:** `DeterministicPlannerStrategy.formulate_decision` routes `DistanceIntent` to `DistanceCapability` and `ResumeActivityIntent` to `ResumeActivityCapability`. Neither is registered in `CapabilityProvider.register_all()`. At runtime, `CapabilityInvoker.invoke("DistanceCapability")` will raise `CapabilityNotFound`. **This is a confirmed crash path for those intents.**

**Evidence path:**  
`DeterministicPlannerStrategy` → `WorkflowRequest(action="DistanceCapability")` → `WorkflowRuntime._execute_step` → `CapabilityInvoker.invoke("DistanceCapability")` → KeyError/NotFound

#### BLOCKER R2 — GGUFInferenceProvider: Model File Not Shipped
**Evidence:** `gguf_provider.py:58` assembles `expected_path` pointing to `desktop/../models/llm/qwen2.5-1.5b-instruct-q4_k_m.gguf`. If this file is absent, `generate()` returns `{"text": "Error: GGUF LLM could not be initialized.", "tool_calls": []}` — a silent string failure. `AIRuntime.resolve_intent()` would then parse an error string as JSON, likely producing `IntentResult(intent="UnknownIntent", confidence=0.05)`.

**Severity:** If the model file is not bundled with the release, the entire `use_llm=True` brain is non-functional.

#### BLOCKER R3 — FasterWhisperProvider.process_audio_stream: Hardcoded Stub
**Evidence:** `faster_whisper_provider.py:107–121`: `process_audio_stream` yields hardcoded `"Hello Chi"` and `"Hello Chitti"` regardless of audio input. If the voice pipeline calls this method (for streaming), all transcriptions will return "Hello Chitti".

**Note:** `_on_transcribe_buffer` correctly calls `process_audio` (not `process_audio_stream`), and `process_audio` is real. The streaming method is only a partial stub. Risk is LOW-MEDIUM.

---

### Q2. Which blockers were false positives?

| False Positive | Reason |
|---|---|
| `MockLLMProvider`, `MockSpeechProvider`, `MockWakeWordProvider` as production risks | These are only imported in test files. Production uses `GGUFInferenceProvider`, `FasterWhisperProvider`, `OpenWakeWordProvider`. |
| `LaunchApplicationCapability` (application.py) as production risk | The canonical `execution.py` version is correctly registered. The legacy file is unreachable. |
| `ExpressionRuntime` (behavior layer ABCs) | The production `ExpressionRuntime` in `runtimes/` is fully functional. The `behavior/` ABCs are unrelated interface blueprints. |
| `Environment Adapters` as core blockers | Not wired into any production capability. Enhancement feature only. |
| `DesktopActivityRuntime` as broken | The implementation is real. Only the boot wiring is missing. Not a core V2 feature. |
| `LiteOCRProvider` as critical blocker | Not wired into production execution path. Screen understanding is a feature enhancement. |

---

### Q3. Which blockers are test-only?

| Component | Evidence |
|---|---|
| `MockLLMProvider` (inference) | Imported only in `tests/test_inference.py`, `app/test_planners.py` |
| `MockLLMProvider` (services) | No production imports |
| `MockWakeWordProvider` | No production imports |
| `MockSpeechProvider` | No production imports |
| `DesktopActivityRuntime` (as used) | Only exercised via `verify_s32b_desktop_activity.py` with `MockContext` |

---

### Q4. Which blockers are configuration-only?

| Component | Configuration Required |
|---|---|
| `GGUFInferenceProvider` | Model file `qwen2.5-1.5b-instruct-q4_k_m.gguf` must exist at `desktop/../models/llm/` |
| `OpenWakeWordProvider` | `openwakeword` package + ONNX runtime must be installed |
| `FasterWhisperProvider` | `faster_whisper` package installed; whisper model available |
| `PiperProvider` | `piper-tts` package + `.onnx` voice model file at configured path |
| `VoiceTransport` | `--use-llm` flag must be explicitly passed to `main.py` |

---

### Q5. What truly prevents CHITTI V2 from shipping?

**Exactly two confirmed functional gaps exist in the production execution path:**

**GAP 1 — Capability Registration Mismatch**  
`DeterministicPlannerStrategy` routes `DistanceIntent` and `ResumeActivityIntent` to capabilities that are not registered in `CapabilityProvider`. Any user utterance that triggers these intents will crash at capability invocation.

**Minimum repair:** Register `DistanceCapability` and `ResumeActivityCapability` in `CapabilityProvider.register_all()`, OR remove these routing branches from `DeterministicPlannerStrategy` for the V2 release.

**GAP 2 — Model/Package Deployment**  
The production system requires `llama_cpp`, `openwakeword`, `faster_whisper`, and `piper-tts` packages plus model files. If these are not validated as present in the release package, boot succeeds silently but the brain (LLM inference) and voice pipeline are non-functional.

**Minimum repair:** Add a startup health check that validates model file existence and package installation, failing loudly (not silently) if critical dependencies are missing.

---

### Q6. What is the exact order they should be repaired?

| Order | Repair | Reason |
|---|---|---|
| 1 | Fix `DistanceCapability` and `ResumeActivityCapability` registration or remove from planner routing | Prevents confirmed crash path for DistanceIntent and ResumeActivityIntent |
| 2 | Add startup dependency/model validation with loud failure | Prevents silent broken state on release machines without model files |
| 3 | Fix `FasterWhisperProvider.process_audio_stream` hardcoded stub | Prevents voice streaming returning "Hello Chitti" for all input |
| 4 | Implement `LLMPlannerStrategy` | Enables dynamic plan formulation. Required for production intelligence but not for current demo scenarios |
| 5 | Register `DistanceCapability` with real geographic API | Functional capability for distance queries |
| 6 | Register `OCRCapability` + implement `LiteOCRProvider` | Screen understanding feature |
| 7 | Implement `PyAutoGUIEngine` + `PlaywrightEngine` | Desktop automation feature |
| 8 | Wire `DesktopActivityRuntime` in `compose_runtimes()` | Analytics feature |

---

## FINAL VERDICT

> **Can CHITTI V2 ship today?**  
> **NO — but for a much narrower reason than the RG01 report suggested.**

The system is architecturally sound and the core AI pipeline (text input → LLM intent resolution → capability execution → expression rendering) works correctly end-to-end **when model files are present**.

The two confirmed release blockers are:
1. **Capability registration gap** (DistanceCapability, ResumeActivityCapability not registered) — causes runtime crash for those intents
2. **Silent model/package dependency failure** — no startup validation ensures the production brain is actually loaded

All other items in the RG01 backlog are either **false positives** (mocks not in production path), **feature enhancements** (OCR, environment adapters), or **configuration requirements** (model file paths).
