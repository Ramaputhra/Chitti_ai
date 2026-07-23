# Implementation Checklist: Component & AI Architecture v1.0.2

- `[x]` **Phase 1: Contracts & Payloads**
- `[x]` **Phase 2: Infrastructure (Component System)**
- `[x]` **Phase 2.5: Mock Provider & E2E Validation**

- `[/]` **Phase 3: ModernBERT Integration (Desktop Intent)**
  - `[x]` Implement lightweight `desktop/platform/benchmark/` utility (latency, RAM/CPU peaks, throughput).
  - `[x]` Create `TextClassificationProvider` (model-agnostic adapter).
  - `[x]` Create `Capability Registry` (Maps string intents to Python capabilities).
  - `[x]` Create `desktop/data/training/intent_dataset.jsonl` for continuous learning from Day 1.
  - `[x]` Implement `IntentService.classify()` with strict Confidence Rules (>=0.95 execute, <0.75 fallback).
  - `[x]` Run the **Desktop Intent Test Suite** (10 canonical commands).
  - `[x]` **Capability Demonstration:** E2E "Open Downloads" (Intent -> Registry -> Execute -> Log -> Done).
  
- `[x]` **Phase 3.5: Experience Learning Engine (The Learning Loop)**
  - `[x]` Initialize SQLite schemas (`experiences`, `experience_patterns`, `experience_stats`, `experience_context`, `experience_embeddings`).
  - `[x]` Implement `ExperienceResolver` (Exact -> Pattern -> Semantic routing).
  - `[x]` Implement `ExperienceLearningEngine` orchestrator and connect to `IntentService`.
  - `[x]` Implement Confidence Evolution scoring logic.
  - `[x]` Save successful, verified procedures back to SQLite.

- `[/]` **Phase 4: Cloud AI & Routing (ADR Execution)**
  - `[x]` **4.1 Policy & Security Foundations**
    - `[x]` Implement `Hardware Profiler` and `CapabilityProfile` models.
    - `[x]` Implement `Credential Manager` (Windows DPAPI).
    - `[x]` Implement `Execution Policy Runtime`.
  - `[x]` **4.2 Remote Infrastructure (Cloud/LAN/MCP)**
    - `[x]` Create `remote_provider.py` (Models, Capabilities, States, RetryPolicy).
    - `[x]` Create `remote_registry.py` (RemoteProviderRegistry).
    - `[x]` Create `remote_session.py` (Session pooling, Circuit Breaker).
    - `[x]` Create `openrouter.py` (OpenRouter Adapter, Tri-state health checks).
    - `[x]` Create `remote_runtime.py` (Stateless Execution Engine).
  - `[x]` **4.3 The Adaptive AI Router**
    - `[x]` Create `routing_models.py` (RoutingDecision, PrivacyLevel, ExecutionMode).
    - `[x]` Create `provider_selector.py` (Rank/Filter logic).
    - `[x]` Create `routing_telemetry.py` (EventBus publisher).
    - `[x]` Create `ai_router.py` (AdaptiveAIRouter).
    - `[x]` Update `PROJECT_STATUS.md` with new Phase 5 breakdown.
  - `[x]` **4.4 Adaptive Learning Runtime (ALR)**
    - `[x]` Create `alr_models.py` (Risk, Version, Candidate, Workflow).
    - `[x]` Create `alr_services.py` (Safety, Generalizer, Reviewer, Promoter).
    - `[x]` Create `capability_registry.py` (Built-in, Learned, Imported).
    - `[x]` Create `adaptive_learning.py` (ALR Orchestrator).
  - `[ ]` **4.5 User Experience & Observability**
    - `[ ]` AI Observability (Runtime stats, provider health dashboard).

- `[ ]` **Phase 5: Building Experiences**
  - `[ ]` **5.1 Listen**: Implement Wake Word, VAD, and STT pipeline.
  - `[ ]` **5.2 Understand**: Implement Semantic Intent & Entity Services.
  - `[ ]` **5.3 Act**: Execute desktop commands via Planner.
  - `[ ]` **5.4 Respond**: Synthesize TTS & display Avatar state.
  - `[ ]` **Experience 001 Validation:** Complete "Chitti, open Downloads" end-to-end.
  
  *(Note: A Capability Demonstration is permanently required to exit any phase. The model is never the milestone; the capability is.)*

- `[ ]` **Phase 5: Refactoring**
  - `[ ]` Rip out all handcrafted legacy AI logic.
