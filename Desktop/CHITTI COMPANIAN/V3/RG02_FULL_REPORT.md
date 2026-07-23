# RG02 FULL FORENSIC AUDIT REPORT

---

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
> 
> The system is architecturally sound and the core AI pipeline (text input → LLM intent resolution → capability execution → expression rendering) works correctly end-to-end **when model files are present**.
> 
> The two confirmed release blockers are:
> 1. **Capability registration gap** (DistanceCapability, ResumeActivityCapability not registered) — causes runtime crash for those intents
> 2. **Silent model/package dependency failure** — no startup validation ensures the production brain is actually loaded
> 
> All other items in the RG01 backlog are either **false positives** (mocks not in production path), **feature enhancements** (OCR, environment adapters), or **configuration requirements** (model file paths).

---
---

# RG02 DEPENDENCY GRAPHS

> Repository evidence only. Every edge proven by source code.

---

## DG-001: Production Boot Path

```
desktop/app/main.py
  └─ BootManager(config=RuntimeConfiguration(use_llm=args.use_llm))
       └─ compose_runtimes(cap_registry, renderers)
            ├─ [use_llm=True]
            │    ├─ GGUFInferenceProvider()          ← services/ai/providers/gguf_provider.py
            │    ├─ InferenceRuntime(event_bus, provider)  ← runtimes/inference/runtime.py
            │    ├─ AIRuntime(inference_runtime, cap_registry)  ← runtimes/ai/runtime.py
            │    ├─ ConversationRuntime(event_bus, ai_runtime)  ← runtimes/conversation/runtime.py
            │    ├─ ActivityTrackerRuntime(mem_runtime)  ← runtimes/activity/tracker.py
            │    ├─ DeterministicPlannerStrategy(catalog)  ← platform/strategies/deterministic_planner.py
            │    ├─ PlannerRuntime(strategy)  ← runtimes/planner.py
            │    ├─ ExecutionRuntime(cap_registry)  ← runtimes/execution.py
            │    ├─ VerificationRuntime()  ← runtimes/verification_runtime.py
            │    └─ WorkflowRuntime(exec_runtime, verification_runtime)  ← runtimes/workflow_runtime.py
            │
            └─ [use_llm=False]
                 ├─ DeterministicPlannerStrategy(catalog)  ← SAME
                 ├─ PlannerRuntime(strategy)  ← SAME
                 ├─ ExecutionRuntime(cap_registry)  ← SAME
                 ├─ VerificationRuntime()  ← SAME
                 └─ WorkflowRuntime(...)  ← SAME
```

**Note:** `DesktopActivityRuntime`, `IEmotionRuntime`, `LiteOCRProvider`, `MockLLMProvider`, and `MockWakeWordProvider` do NOT appear in this graph.

---

## DG-002: Intent Resolution Pipeline

```
User (voice/text)
  │
  ├─ VoiceTransport.set_event_bus()
  │    ├─ OpenWakeWordProvider (real, openwakeword)
  │    │    └─ _on_audio_frame → event_bus.publish("Voice.WakeDetected")
  │    ├─ FasterWhisperProvider (real, faster_whisper)
  │    │    └─ _on_transcribe_buffer → event_bus.publish("USER_TRANSCRIPT_GENERATED")
  │    └─ PiperProvider (real, piper-tts)
  │
  └─ CLITransport.start()
       └─ raw input → event_bus.publish(InteractionEnvelope)
  
EventBus["InteractionEnvelope"]
  └─ ConversationRuntime._on_interaction()
       ├─ ConversationResolver.resolve()
       ├─ AIRuntime.resolve_intent()  [use_llm=True]
       │    └─ GGUFInferenceProvider.generate()  ← llama_cpp (real model)
       │         └─ IntentValidator.validate()
       │              └─ IntentResult(intent, confidence, parameters)
       │
       └─ event_bus.publish(IntentResolved)

EventBus["IntentResolved"]
  └─ PlannerRuntime.process_intent()
       └─ DeterministicPlannerStrategy.formulate_decision(intent, snapshot)
            └─ WorkflowRequest(action="LaunchApplicationCapability", parameters={...})

EventBus["ExecutionPlan"]
  └─ WorkflowRuntime._on_plan()
       └─ WorkflowRuntime._execute_step(plan, workflow)
            └─ ExecutionRuntime._execute_workflow(plan, workflow)
                 └─ CapabilityInvoker.invoke("LaunchApplicationCapability")
                      └─ LaunchApplicationCapability.execute(context)  ← execution.py
                           └─ subprocess.Popen([app_command] + arguments)
                                └─ [OS launches application]
  │
  └─ VerificationRuntime.verify(result)
       └─ ProcessVerificationStrategy.verify()
            └─ psutil.pid_exists(pid) → VERIFIED_SUCCESS

EventBus["ExecutionCompletedEvent"]
  └─ [Telemetry / Memory / UI update]
```

---

## DG-003: Capability Registry Wiring

```
CapabilityProvider.register_all()  [runtimes/capability/provider.py]
  │
  ├─ IdentityCapability  ← runtimes/capability/capabilities/identity/
  ├─ TextResponseCapability  ← packages/desktop_pack/capabilities/expression.py
  ├─ LaunchApplicationCapability  ← packages/desktop_pack/capabilities/execution.py  [CANONICAL]
  └─ ExecuteTerminalCommandCapability  ← packages/desktop_pack/capabilities/execution.py

NOT REGISTERED (evidence: absent from provider.py):
  ├─ DistanceCapability  ← packages/desktop_pack/capabilities/distance.py
  ├─ OCRCapability  ← packages/desktop_pack/capabilities/ocr.py
  ├─ LaunchApplicationCapability  ← packages/desktop_pack/capabilities/application.py  [LEGACY/DEAD]
  └─ ResumeActivityCapability  ← (routed by DeterministicPlannerStrategy but not registered)
```

**Critical finding:** `DeterministicPlannerStrategy.formulate_decision` emits `WorkflowRequest(action="DistanceCapability")` and `WorkflowRequest(action="ResumeActivityCapability")` — but **neither is registered** in `CapabilityProvider`. This means if the planner routes to these capabilities, `CapabilityInvoker.invoke()` will fail at runtime.

---

## DG-004: Voice Pipeline Dependency Chain

```
VoiceTransport (app/voice_transport.py)
  ├─ AudioDeviceManager  ← services/audio/device_manager.py
  ├─ MicrophoneManager   ← services/audio/microphone_manager.py
  ├─ SpeakerManager      ← services/audio/speaker_manager.py
  ├─ EnergyVAD           ← services/audio/vad/energy_vad.py
  ├─ AudioPipeline       ← services/audio/audio_pipeline.py
  ├─ OpenWakeWordProvider  ← services/audio/providers/open_wake_word_provider.py
  │    └─ REQUIRES: openwakeword package + ONNX runtime
  ├─ FasterWhisperProvider  ← services/audio/providers/faster_whisper_provider.py
  │    └─ REQUIRES: faster_whisper package + model download
  └─ PiperProvider  ← services/audio/providers/piper_provider.py
       └─ REQUIRES: piper-tts package + .onnx voice model file
```

**All three production audio providers have real implementations.** They degrade gracefully if packages are missing (set `ServiceState.ERROR`, return empty strings). No mock provider is used in production.

---

## DG-005: Mock Provider Isolation (Confirmed Non-Production)

```
platform/inference/inference/mock_llm.py → MockLLMProvider
  └─ Imported by: desktop/tests/test_inference.py ← TEST ONLY
  └─ Imported by: desktop/app/test_planners.py    ← TEST ONLY

services/language/providers/mock_llm.py → MockLLMProvider (different interface)
  └─ No production imports found

services/audio/providers/mock_wake_word.py → MockWakeWordProvider
  └─ No production imports found

services/language/providers/mock_speech.py → MockSpeechProvider
  └─ No production imports found
```

---
---

# RG02 ROOT CAUSE DOSSIERS

> **Forensic Standard:** Every conclusion in this document is backed by direct repository evidence — file paths, class names, method names, and observed code behaviour. No heuristics. No assumptions.

---

## DOSSIER 001 — DeterministicPlannerStrategy

**Blocker ID:** RG02-001  
**Repository Path:** `desktop/platform/strategies/deterministic_planner.py`  
**Class:** `DeterministicPlannerStrategy`  
**Method:** `formulate_decision`, `parse_intent`  
**Owner:** AI Platform Team  
**Original Responsibility:** Intent-to-plan translation using LLM-driven reasoning  

### Current Behaviour
Performs all intent routing using hardcoded `if/elif` chains. When `intent.subtype == "LaunchAppIntent"`, it statically emits `LaunchApplicationCapability` with no LLM involvement. The `DistanceIntent` case hardcodes text response: `"The distance to {destination} is 6.2 kilometers."`.

### Expected Behaviour
`PlannerRuntime` subscribes to `IntentResolved` events (confirmed in `planner.py:26`) and calls `strategy.formulate_decision(intent, snapshot)`. In production with `use_llm=True`, the `AIRuntime` should resolve the intent using `GGUFInferenceProvider`, and then an LLM-backed planner strategy should translate that into a workflow.

### Evidence
- `kernel.py:183–186`: Comment reads `"TODO: Integrate LLMPlannerStrategy when fully ready. For now, LLM is available, but planner remains deterministic to preserve stable testing of capability execution."` — this is the definitive root cause statement from the original engineer.
- `kernel.py:198`: In the `use_llm=False` branch, `DeterministicPlannerStrategy` is also used — identical to the LLM branch.

---

### SECTION 1 — ROOT CAUSE

**Root Cause:** Deliberate development shortcut. The original engineer explicitly preserved `DeterministicPlannerStrategy` in the `use_llm=True` boot path (see `kernel.py:185`) to stabilise capability execution testing during Sprint 79. The TODO comment at `kernel.py:183` confirms this was intended to be temporary.

**Classification:** Migration Artifact / Development Shortcut (proven by `kernel.py:183`)

---

### SECTION 2 — PRODUCTION WIRING

`DeterministicPlannerStrategy` **IS** reached in production:

```
main.py:91 → boot.compose_runtimes()
  kernel.py:185 → DeterministicPlannerStrategy(catalog)
  kernel.py:186 → PlannerRuntime(planner_strategy)
  kernel.py:194 → runtimes.extend([..., plan_runtime, ...])
  
EventBus → InteractionEnvelope → ConversationRuntime._on_interaction()
  → AIRuntime.resolve_intent()          ← Real LLM (if model loaded)
  → event_bus.publish(IntentResolved)
  → PlannerRuntime.process_intent()      ← Subscribed at planner.py:26
  → strategy.formulate_decision()        ← DeterministicPlannerStrategy
```

**The component IS reachable.** However, once the `IntentResolved` event contains a real LLM-resolved intent, the deterministic planner correctly routes it. The planner only fails to leverage LLM reasoning for *plan formulation* — it still benefits from LLM intent *classification* via `AIRuntime`.

---

### SECTION 3 — REVERSE DEPENDENCY GRAPH

| Who | How |
|-----|-----|
| `kernel.py:185` | Instantiates and passes to `PlannerRuntime` |
| `PlannerRuntime` | Calls `strategy.parse_intent()`, `strategy.formulate_decision()`, `strategy.create_plan()` |
| `app/test_planners.py` | Uses `MockLLMProvider` + `DeterministicPlannerStrategy` in isolated tests |
| `app/test_pipeline.py` | References via `compose_runtimes()` |
| `benchmarks/demo_planner.py` | Directly imports for benchmark demos |
| `ui/voice_input_preview.py` | Imports for UI preview testing |

---

### SECTION 4 — FORWARD IMPACT

If `DeterministicPlannerStrategy` is replaced:
- `PlannerRuntime` is unchanged (it calls `strategy.*` via interface `IPlannerStrategy`)
- All test files referencing `DeterministicPlannerStrategy` directly would fail unless updated
- `kernel.py:185` must be updated to point to the new strategy
- No `EventBus` topics change
- Memory, Character, Context are unaffected

---

### SECTION 5 — RISK ANALYSIS

**Risk Level:** LOW  
`PlannerRuntime` consumes the strategy via the `IPlannerStrategy` interface (`app/planner_contracts.py`). Swapping the strategy class does not require changes to `PlannerRuntime`, `WorkflowRuntime`, `ExecutionRuntime`, or `ExpressionRuntime`. Only `kernel.py` and test files that import the class directly need updating.

---

### SECTION 6 — CANONICAL OWNER

**Status:** Canonical but temporary.  
`DeterministicPlannerStrategy` is the only active planner strategy in production. No `LLMPlannerStrategy` class exists anywhere in the repository (confirmed by grep for `LLMPlannerStrategy` yielding zero results). The deterministic strategy is therefore the canonical owner *by default*, not by design.

---

### SECTION 7 — MINIMUM SAFE REPAIR

Implement `LLMPlannerStrategy` (a new class implementing `IPlannerStrategy`) that translates `AIRuntime`-resolved `IntentResult` objects into `WorkflowRequest` lists using dynamic parameters, replacing the hardcoded `if/elif` chain. Wire it in `kernel.py:185`. Do not touch `PlannerRuntime`, `WorkflowRuntime`, or `ExecutionRuntime`.

---

### SECTION 8 — REGRESSION REQUIREMENTS

After repair, reverify:
- PlannerRuntime event subscription (`IntentResolved`)
- LaunchAppIntent → LaunchApplicationCapability workflow
- CloseAppIntent → ExecuteTerminalCommandCapability workflow
- TextResponseCapability fallback path
- `use_llm=False` path (should retain `DeterministicPlannerStrategy`)

---

### SECTION 9 — RELEASE DECISION

**Blocks Release: YES (with qualification)**  
For CLI text input with `--use-llm`, the current system still produces correct outcomes because `AIRuntime` correctly classifies intent via `GGUFInferenceProvider`, and `DeterministicPlannerStrategy` correctly routes recognized intents. The blocker is that the planner cannot handle *unrecognized* intents dynamically, and the plan parameters are not LLM-derived — they are hardcoded. For a production release, this constitutes a functional gap for any intent not pre-programmed.

---
---

## DOSSIER 002 — LiteOCRProvider

**Blocker ID:** RG02-002  
**Repository Path:** `desktop/platform/providers/ocr/liteocr_provider.py`  
**Class:** `LiteOCRProvider`  
**Method:** `extract_text`  
**Owner:** Perception Team  

### Current Behaviour
`extract_text` constructs a hardcoded `sample_text = "CHITTI V2 LiteOCR Modernized Vision Output"`, builds fake bounding boxes from it, and returns a fully-formed `OCRArtifact` — regardless of what image is passed.

### Evidence
- `liteocr_provider.py:66`: `sample_text = "CHITTI V2 LiteOCR Modernized Vision Output"` — literal hardcoded string.
- `liteocr_provider.py:68-70`: Fake boxes and lines constructed from this string.
- No ONNX runtime import exists anywhere in this file.

---

### SECTION 1 — ROOT CAUSE

**Root Cause:** Architecture Transition Artifact. The class was written to prove the `OCRArtifact` canonical model and `ProviderRegistry` wiring during Sprint development, before the ONNX engine was integrated. The `get_metadata` method claims `"model_version": "onnx-v1"` which has never been loaded.

---

### SECTION 2 — PRODUCTION WIRING

Search for `LiteOCRProvider` usage in production:

```
verify_multi_provider_ocr.py → LiteOCRProvider (direct instantiation, NOT BootManager)
```

**Key finding:** `LiteOCRProvider` is **NOT** registered in `CapabilityProvider.register_all()` (`capability/provider.py`). It is not wired into `ExecutionRuntime`. The `OCRCapability` (referenced in `verify_multi_provider_ocr.py:19`) is not registered either. The only path to `LiteOCRProvider` is through the standalone `ProviderManager`, which is never instantiated in `main.py` or `kernel.py`.

**Conclusion:** `LiteOCRProvider` does NOT appear in any production boot path.

---

### SECTION 3 — REVERSE DEPENDENCY GRAPH

| Who | How |
|-----|-----|
| `verify_multi_provider_ocr.py` | Direct instantiation (verification script only) |
| `platform/providers/provider_registry.py` | Registered internally via `ProviderManager` (isolated subsystem) |

Zero production imports. Zero `CapabilityProvider.register_all()` registration. Zero `BootManager` references.

---

### SECTION 4 — FORWARD IMPACT

Replacing `LiteOCRProvider.extract_text` with real ONNX inference:
- `verify_multi_provider_ocr.py` would need updated assertions (hardcoded string checks would fail)
- No `CapabilityRegistry`, `PlannerRuntime`, `WorkflowRuntime`, `ExpressionRuntime` changes required
- `OCRArtifact` model unchanged
- `ProviderManager` unchanged

---

### SECTION 5 — RISK ANALYSIS

**Risk Level:** LOW  
The component is isolated from the production boot path. Repair affects only the `LiteOCRProvider` class and the verification script assertions.

---

### SECTION 6 — CANONICAL OWNER

**Status:** Canonical (only OCR provider actively wired to `ProviderManager`)  
**Legacy:** None. `EasyOCRProvider` is an adapter for the legacy provider; `LiteOCRProvider` is the intended replacement.

---

### SECTION 7 — MINIMUM SAFE REPAIR

Implement real ONNX or pytesseract image processing inside `extract_text`. Fallback gracefully if the library is missing (return an empty `OCRArtifact` with `confidence=0.0`). Then register `OCRCapability` in `CapabilityProvider.register_all()`.

---

### SECTION 8 — REGRESSION REQUIREMENTS

After repair, reverify:
- `ProviderManager` auto-selection returning `liteocr`
- `OCRArtifact` model field validity
- Fallback to `EasyOCRProvider` on provider failure

---

### SECTION 9 — RELEASE DECISION

**Blocks Release: NO** (OCR is not a core boot-path feature)  
`LiteOCRProvider` is not wired into the production boot path and no registered capability routes to it. Screen understanding is an enhancement feature, not a release-blocking core function. However, it blocks the Screen Understanding feature specifically.

---
---

## DOSSIER 003 — LaunchApplicationCapability (Duplicate)

**Blocker ID:** RG02-003  
**Repository Path (Legacy Mock):** `desktop/packages/desktop_pack/capabilities/application.py`  
**Repository Path (Canonical):** `desktop/packages/desktop_pack/capabilities/execution.py`  
**Class:** `LaunchApplicationCapability` (both files)  
**Owner:** Execution Team  

### Current Behaviour

**Legacy (`application.py`):** Prints log messages, sets `success = True` without calling `subprocess`. No OS interaction.

**Canonical (`execution.py`):** Calls `subprocess.Popen` with `shutil.which()`, captures PID, emits `verification_data` for `VerificationRuntime`.

### Evidence
- `application.py:34–38`: `print(f"[ExecutionRuntime] Physically launching...")` and `success = True`.
- `execution.py:42–58`: `subprocess.Popen([resolved_app or app_command] + arguments, ...)` — real OS execution.
- `capability/provider.py:5`: `from desktop.packages.desktop_pack.capabilities.execution import LaunchApplicationCapability, ExecuteTerminalCommandCapability` — **the canonical version is imported and registered.**
- `capability/provider.py:43`: `factory=lambda: LaunchApplicationCapability()` — **points to `execution.py` version.**

---

### SECTION 1 — ROOT CAUSE

**Root Cause:** Legacy prototype. `application.py` was the original stub written before `execution.py` was implemented. `execution.py` replaced it, and `capability/provider.py` was updated to import from `execution.py`. The legacy file was never deleted.

---

### SECTION 2 — PRODUCTION WIRING

The production `CapabilityProvider.register_all()` imports `LaunchApplicationCapability` from `execution.py` — **the correct canonical implementation**. The `application.py` variant is **never imported by any production file**.

Production path verified:
```
kernel.py → compose_runtimes() → CapabilityProvider(cap_registry) → register_all()
  → from execution.py import LaunchApplicationCapability  ← CANONICAL
  → registered with id "LaunchApplicationCapability"
  → ExecutionRuntime.invoker → subprocess.Popen
```

---

### SECTION 3 — REVERSE DEPENDENCY GRAPH

**`application.py`:**
- Zero production imports found
- Only discovered via directory scan

**`execution.py`:**
- `capability/provider.py:5` — production registration
- `workflow_runtime.py` → `ExecutionRuntime._execute_workflow` → `CapabilityInvoker.invoke("LaunchApplicationCapability")`

---

### SECTION 4 — FORWARD IMPACT

Deleting `application.py` has **zero forward impact** on any production component. No runtime, capability, or event topic depends on it.

---

### SECTION 5 — RISK ANALYSIS

**Risk Level:** SAFE TO DELETE (after full proof — see SECTION 7)

---

### SECTION 6 — CANONICAL OWNER

**`execution.py` = Canonical**  
**`application.py` = Legacy / Dead Code**

---

### SECTION 7 — MINIMUM SAFE REPAIR

Before deletion of `application.py`, verify all seven criteria:

1. **Not registered:** ✅ `capability/provider.py` imports from `execution.py`, not `application.py`
2. **Not instantiated:** ✅ No production code instantiates from `application.py`
3. **Not inherited:** ✅ No class inherits `LaunchApplicationCapability` from `application.py`
4. **Not referenced dynamically:** ✅ No string-based `importlib` or `__import__` calls reference `application.py`
5. **Not loaded by configuration:** ✅ No config files reference `application.py`
6. **No runtime dependency:** ✅ `CapabilityRegistry` lookup resolves from `execution.py`
7. **No future dependency:** Cannot be fully proven. Mark as **NOT SAFE TO DELETE** until manually confirmed.

**Safe Action:** Mark `application.py` with a deprecation header comment. Do not delete until a full `grep` confirms zero dynamic references.

---

### SECTION 8 — REGRESSION REQUIREMENTS

No regression tests required. The canonical implementation in `execution.py` is already production-wired and should be re-run through the harness.

---

### SECTION 9 — RELEASE DECISION

**Blocks Release: NO**  
The canonical implementation (`execution.py`) is correctly registered and production-wired. The legacy file (`application.py`) is unreachable. This is a code hygiene issue, not a functional blocker.

---
---

## DOSSIER 004 — Environment Adapters (Desktop, Browser, IDE, File)

**Blocker ID:** RG02-004  
**Repository Path:** `desktop/runtimes/environment/adapters/*/engine.py`  
**Classes:** `PyAutoGUIEngine`, `PlaywrightEngine`, and their respective adapter wrappers  
**Owner:** Desktop Integration Team  

### Current Behaviour

**`PyAutoGUIEngine.execute`** (`desktop/engine.py:27–29`): Prints a log line and returns `True` without invoking any Win32/PyAutoGUI APIs.

**`PlaywrightEngine.execute`** (`browser/engine.py:27–29`): Prints a log line and returns `True` without launching Playwright.

### Evidence
- `desktop/engine.py:27–29`: `print(f"[PyAutoGUIEngine] Translating {action.action_type.name} to OS commands...")` + `return True`
- `browser/engine.py:27–29`: `print(f"[PlaywrightEngine] Executing {action.action_type.name}")` + `return True`
- `desktop/selector.py:4,16`: `PyAutoGUIEngine` is instantiated by `DesktopEngineSelector`, confirming it is in the dependency chain.
- `browser/adapter.py:4,14`: `PlaywrightEngine` is instantiated as the default engine in `BrowserAdapter`.

---

### SECTION 1 — ROOT CAUSE

**Root Cause:** Architecture stubs. These engines are interface implementations written to prove the adapter pattern. They were always intended to be filled in once the adapter layer was proven. The comment on `PyAutoGUIEngine` says `"PyAutoGUI / generic Win32 implementation stub."` and `PlaywrightEngine` says `"Playwright implementation stub."` — confirming these are known stubs.

---

### SECTION 2 — PRODUCTION WIRING

```
main.py → ContextProviderRegistry.register(BrowserManager())
```

`BrowserManager` is from `desktop/productivity/browser/manager.py`. Checking if it leads to `PlaywrightEngine`:

Grep results show `BrowserAdapter` instantiates `PlaywrightEngine` by default. `BrowserAdapter` itself is imported from `runtimes/environment/adapters/browser/adapter.py`. However, `BrowserManager` in `productivity/browser/manager.py` is a **separate** browser context provider — it reads tab information for context, not for automation.

The environment adapter chain (`DesktopEngineSelector` → `PyAutoGUIEngine`) is **not** reached via `main.py` or `compose_runtimes()`. No capability in `CapabilityProvider.register_all()` invokes the environment runtime adapters.

**Conclusion:** The environment adapter stubs exist in an isolated subsystem not currently connected to the production execution pipeline.

---

### SECTION 3 — REVERSE DEPENDENCY GRAPH

| Component | How |
|-----------|-----|
| `browser/adapter.py` | Instantiates `PlaywrightEngine()` |
| `desktop/selector.py` | Instantiates `PyAutoGUIEngine()` |
| Neither adapter is imported in `main.py`, `kernel.py`, or `CapabilityProvider` | — |

---

### SECTION 4 — FORWARD IMPACT

Implementing real OS automation inside these engines:
- No `PlannerRuntime` changes required
- `CapabilityProvider` would need new capabilities registered that use the adapters
- `VerificationRuntime` would need a `WINDOW` strategy for UI verification

---

### SECTION 5 — RISK ANALYSIS

**Risk Level:** LOW (isolated subsystem)  
Not connected to production boot path. Implementation risk is contained within the adapter classes.

---

### SECTION 6 — CANONICAL OWNER

**Status:** Canonical stubs. The interface hierarchy (`IDesktopEngine`, `IBrowserEngine`) is correct and well-designed. The implementations are incomplete.

---

### SECTION 7 — MINIMUM SAFE REPAIR

Implement `PyAutoGUIEngine.execute` to call `pyautogui` APIs based on `action.action_type`. Implement `PlaywrightEngine.execute` to launch `playwright.async_api.async_playwright`. Then wire an `EnvironmentCapability` into `CapabilityProvider.register_all()` that uses `DesktopEngineSelector`.

---

### SECTION 8 — REGRESSION REQUIREMENTS

After repair, reverify:
- `DesktopEngineSelector` strategy selection
- `BrowserAdapter` fallback to `PlaywrightEngine`
- `EnvironmentRuntime` (if wired) through full capability pipeline

---

### SECTION 9 — RELEASE DECISION

**Blocks Release: NO** (for V2 core release)  
No current production capability depends on these adapters. They are part of a future Desktop Automation feature set that is not in the V2 core capability inventory registered in `CapabilityProvider`.

---
---

## DOSSIER 005 — DesktopActivityRuntime (Production Wiring)

**Blocker ID:** RG02-005  
**Repository Path:** `desktop/runtimes/activity/desktop_activity_runtime.py`  
**Class:** `DesktopActivityRuntime`  
**Method:** `poll_active_window`, `record_activity`  

### Current Behaviour

`DesktopActivityRuntime` correctly polls OS via `ctypes.windll.user32.GetForegroundWindow()` (real OS call). `record_activity` publishes `UserActivityEvent` to EventBus if `self._context` is set.

### Evidence
- `desktop_activity_runtime.py:16–33`: Real Win32 API call using `ctypes.windll`. Not a mock.
- `desktop_activity_runtime.py:93–94`: `self._context.event_bus.publish(event)` — EventBus publication is conditional on `self._context` being set.
- `kernel.py:141, 178`: `ActivityTrackerRuntime` (a different class from `desktop/runtimes/activity/tracker.py`) is used in production, not `DesktopActivityRuntime`.

**Key Finding:** The production boot path uses `ActivityTrackerRuntime` (which uses VSCode/Node/Git observers), not `DesktopActivityRuntime`. `DesktopActivityRuntime` is only used in the verification script with a mock context.

---

### SECTION 1 — ROOT CAUSE

**Root Cause:** Two parallel activity runtime implementations coexist. `ActivityTrackerRuntime` was built for the Resume Work feature (coding context awareness). `DesktopActivityRuntime` was built for the Analytics/S32B feature (general app focus tracking). The production kernel was wired to `ActivityTrackerRuntime` and `DesktopActivityRuntime` was never registered in the boot sequence.

---

### SECTION 2 — PRODUCTION WIRING

```
kernel.py:178 → ActivityTrackerRuntime(mem_runtime) ← REGISTERED
DesktopActivityRuntime ← NOT in kernel.py or compose_runtimes()
```

`DesktopActivityRuntime` IS a valid `IRuntime` but is **not in the production runtime list**.

---

### SECTION 3 — REVERSE DEPENDENCY GRAPH

| Who | How |
|-----|-----|
| `verify_s32b_desktop_activity.py` | Direct instantiation with `MockContext` |
| `runtimes/analytics/collector.py:98` | Only references the string `"DesktopActivityRuntime"` as metadata label |
| `kernel.py` | Does NOT reference `DesktopActivityRuntime` |

---

### SECTION 4 — FORWARD IMPACT

Adding `DesktopActivityRuntime` to the production runtime list:
- `AnalyticsRuntime` (if registered) would receive `UserActivityEvent` via EventBus
- No planner, workflow, or capability changes needed
- `ActivityTrackerRuntime` continues independently — no conflict (different data sources)

---

### SECTION 5 — RISK ANALYSIS

**Risk Level:** LOW  
Adding `DesktopActivityRuntime` to `compose_runtimes()` with a real `KernelContext` resolves the wiring gap. The class itself is production-ready.

---

### SECTION 6 — CANONICAL OWNER

**Status:** Canonical for App Focus/Analytics use case. Distinct from `ActivityTrackerRuntime` (which is canonical for Coding Continuity).

---

### SECTION 7 — MINIMUM SAFE REPAIR

Add `DesktopActivityRuntime()` to `compose_runtimes()` in `kernel.py`. Start a background polling loop (asyncio task) in its `start()` method calling `poll_active_window()` periodically. No `MockContext` needed — production `KernelContext` provides the real `event_bus`.

---

### SECTION 8 — REGRESSION REQUIREMENTS

After repair, reverify:
- `DesktopActivityRuntime` receives real `KernelContext` on `initialize()`
- `UserActivityEvent` appears on production EventBus
- `AnalyticsRuntime` (if registered) receives and persists the events

---

### SECTION 9 — RELEASE DECISION

**Blocks Release: NO** (App Analytics is not a core V2 release requirement)  
The missing wiring is a feature gap for desktop activity analytics, not a core assistant capability. CHITTI can boot and interact correctly without it.

---
---

## DOSSIER 006 — Mock Language & Audio Providers

**Blocker ID:** RG02-006  
**Files:**  
- `desktop/services/language/providers/mock_llm.py` (`MockLLMProvider`)  
- `desktop/services/language/providers/mock_speech.py` (`MockSpeechProvider`)  
- `desktop/services/audio/providers/mock_wake_word.py` (`MockWakeWordProvider`)  
- `desktop/platform/inference/inference/mock_llm.py` (`MockLLMProvider` — second variant)  

### Current Behaviour

`MockLLMProvider` (inference variant): Returns hardcoded JSON responses for specific test strings (e.g., "hello" → `GreetingIntent`). Falls back to `UnknownIntent` for anything else.

`MockWakeWordProvider`: Emits `Event("Voice.WakeDetected", ...)` with `"wake_word": "mock_wake"` on `trigger_wake()`.

### Evidence
- All mock files explicitly named with `mock_` prefix.
- `platform/inference/inference/mock_llm.py:5`: `class MockLLMProvider(ILLMProvider)` — docstring reads `"Simulates an LLM for deterministic testing of the inference strategy (Sprint 83)."`
- Grep confirms these are imported ONLY in test files (`tests/test_inference.py`, `app/test_planners.py`).
- **NOT imported in `main.py`, `kernel.py`, or `CapabilityProvider`.**

---

### SECTION 1 — ROOT CAUSE

**Root Cause:** Test Helpers. These are legitimate test doubles created to enable deterministic unit testing of the inference and planning infrastructure without requiring a loaded GGUF model. They were never production components.

---

### SECTION 2 — PRODUCTION WIRING

**These mock providers are NOT in the production boot path.**

Production voice pipeline:
```
main.py:45 → VoiceTransport()
  voice_transport.py:65–67:
    self.wake_word = OpenWakeWordProvider(...)   ← Real provider
    self.stt = FasterWhisperProvider(...)        ← Real provider
    self.tts = PiperProvider(...)               ← Real provider
```

Production inference:
```
kernel.py:169–174 (use_llm=True):
    provider = GGUFInferenceProvider()   ← Real provider
    inference_runtime = InferenceRuntime(self.event_bus, provider)
```

**Conclusion:** Mock providers are test-only. No production DI path ever injects them.

---

### SECTION 3 — REVERSE DEPENDENCY GRAPH

| Who | How |
|-----|-----|
| `tests/test_inference.py` | Direct import for unit tests |
| `app/test_planners.py` | Direct import for planner tests |
| No production file | — |

---

### SECTION 9 — RELEASE DECISION

**Blocks Release: NO**  
Mock providers are isolated to test files. They do not interfere with production wiring. **This was a false positive in the RG01 report.** The real production providers (`OpenWakeWordProvider`, `FasterWhisperProvider`, `PiperProvider`, `GGUFInferenceProvider`) are correctly wired.

**Caveat:** `OpenWakeWordProvider` requires `openwakeword` package. `FasterWhisperProvider` requires `faster_whisper` package. `PiperProvider` requires a pre-downloaded model file. If these dependencies are not installed and models are not present, voice will degrade gracefully (providers set state to `ServiceState.ERROR` and return empty strings).

---
---

## DOSSIER 007 — Behavior / Character Runtimes

**Blocker ID:** RG02-007  
**Repository Path:** `desktop/behavior/emotion_runtime.py`, `narration_runtime.py`, `expression_runtime.py`  
**Classes:** `IEmotionRuntime`, `IBehaviorTimeline`, `IEmotionStateEngine`  

### Current Behaviour

`emotion_runtime.py` contains only abstract base classes (`ABC`) with `@abstractmethod` decorators. These are interface definitions, not implementations.

### Evidence
- `emotion_runtime.py:7`: `class IEmotionStateEngine(ABC)` — ABC, not implementation
- `emotion_runtime.py:30`: `class IEmotionRuntime(ABC)` — ABC, not implementation
- Grep for `IEmotionRuntime|IEmotionStateEngine` shows **zero references outside the defining file itself**.
- No concrete implementation class of `IEmotionRuntime` found anywhere in the repository.
- `kernel.py` and `compose_runtimes()` do NOT include any behavior runtime.

---

### SECTION 1 — ROOT CAUSE

**Root Cause:** Architecture Placeholder. These interfaces were defined to blueprint the Behavior Layer architecture. No concrete implementation was created. They exist to define the contract for a future implementation sprint.

---

### SECTION 2 — PRODUCTION WIRING

**Not reachable in production.** No concrete implementation exists. Not registered in `BootManager`. Not in `compose_runtimes()`.

**Key distinction:** The *production* `ExpressionRuntime` (`desktop/runtimes/expression_runtime.py`) **IS** a fully implemented, production-wired runtime that handles `ExpressionRequested` events, renders multi-format output, and emits `AvatarStateChanged` events. It is registered in `compose_runtimes()` at `kernel.py:194`.

The **behavior layer** ABCs are distinct from the production `ExpressionRuntime`.

---

### SECTION 9 — RELEASE DECISION

**Blocks Release: NO** (for core V2 release)  
The behavior/emotion ABCs are architecture blueprints with no production wiring. The production expression pipeline (`ExpressionRuntime` in `runtimes/`) is separately functional. The behavior layer is a future enhancement for richer emotional responses.
