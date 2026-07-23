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
