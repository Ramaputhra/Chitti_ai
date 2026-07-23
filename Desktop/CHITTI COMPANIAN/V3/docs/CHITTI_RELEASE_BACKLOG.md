# CHITTI V2 RELEASE BACKLOG
## DEFINITIVE ENGINEERING BACKLOG (RG01)

This backlog is the single source of truth for all remaining engineering work required to ship CHITTI V2. Every item listed is a release blocker.

---

### ITEM 1: Core AI & Intent Pipeline Implementation
- **Feature:** LLM-based Intent Resolution & Planning
- **Repository Path:** `desktop/platform/strategies/deterministic_planner.py`
- **Owner:** AI Platform Team
- **Category:** C (MOCK)
- **Priority:** P0 (Blocks Release)
- **Release Critical:** YES
- **Evidence:** `DeterministicPlannerStrategy.formulate_decision` bypasses LLM inference, routing hardcoded intents statically.
- **User Impact:** Without this, the assistant cannot dynamically reason, understand natural language intents, or formulate complex plans.
- **Architecture Impact:** Core component. `InferenceRuntime`, `AIRuntime`, and `ConversationRuntime` are completely bypassed.
- **Required Action:** Replace `DeterministicPlannerStrategy` with a production LLM planner strategy. Wire intent resolution through `InferenceRuntime`.

---

### ITEM 2: OCR Engine Integration
- **Feature:** Screen Understanding (LiteOCR)
- **Repository Path:** `desktop/platform/providers/ocr/liteocr_provider.py`
- **Owner:** Perception Team
- **Category:** C (MOCK)
- **Priority:** P0 (Blocks Release)
- **Release Critical:** YES
- **Evidence:** `extract_text` returns a static `OCRArtifact` containing "CHITTI V2 LiteOCR Modernized Vision Output" rather than invoking ONNX/Vision models.
- **User Impact:** Users cannot highlight, translate, or copy text from images or the screen.
- **Architecture Impact:** Downstream capabilities relying on layout trees or canonical OCR artifacts will fail or process dummy data.
- **Required Action:** Implement actual ONNX model inference within `LiteOCRProvider` to parse input images and return real bounding boxes and confidence scores.

---

### ITEM 3: Navigation Intelligence Execution
- **Feature:** Distance & Route Calculation
- **Repository Path:** `desktop/packages/desktop_pack/capabilities/distance.py`
- **Owner:** Capabilities Team
- **Category:** C (MOCK)
- **Priority:** P1 (Critical Feature)
- **Release Critical:** YES
- **Evidence:** `execute` method hardcodes `distance_km = 42.5` and `eta_mins = 45`.
- **User Impact:** All routing and distance queries fail to provide accurate geographical data.
- **Architecture Impact:** `NavigationArtifact` instances contain fabricated `structured_result` payloads, undermining the Context Engine's trust.
- **Required Action:** Integrate a real geographic/routing API to compute dynamic distance and ETA.

---

### ITEM 4: Environment Adapters Implementation
- **Feature:** Contextual OS & App Awareness (Desktop, Browser, IDE, File)
- **Repository Path:** `desktop/runtimes/environment/adapters/*/engine.py`
- **Owner:** Desktop Integration Team
- **Category:** B (PLACEHOLDER)
- **Priority:** P0 (Blocks Release)
- **Release Critical:** YES
- **Evidence:** Target engine implementations primarily contain `pass`, `raise NotImplementedError`, and `# TODO` comments.
- **User Impact:** The assistant cannot actually read active window state, browser DOMs, IDE context, or filesystem changes.
- **Architecture Impact:** `EnvironmentRuntime` cannot supply valid context to `ContextBuilder`, breaking multi-modal awareness.
- **Required Action:** Write native OS integration hooks (e.g., Accessibility APIs, Playwright/CDP) inside the respective environment adapter engines.

---

### ITEM 5: Desktop Activity Runtime Wiring
- **Feature:** User Activity Tracking & Analytics
- **Repository Path:** `desktop/runtimes/activity/desktop_activity_runtime.py` (via `verify_s32b_desktop_activity.py`)
- **Owner:** Analytics Team
- **Category:** D (BROKEN WIRING)
- **Priority:** P0 (Blocks Release)
- **Release Critical:** YES
- **Evidence:** The verification scripts manually inject `MockContext` and `MockEventBus`. The runtime is not definitively registered or proven within the production `BootManager`.
- **User Impact:** CHITTI cannot passively track what projects/apps the user is working on, breaking Goal/Project runtime correlations.
- **Architecture Impact:** `UserActivityEvent` relies on the production EventBus to populate `AnalyticsRuntime`. If unwired, timelines remain empty.
- **Required Action:** Formally register `DesktopActivityRuntime` in the `BootManager` and ensure it subscribes to/publishes to the production `EventBus`.

---

### ITEM 6: Clean Up Duplicate Application Launch Capability
- **Feature:** Local App Execution
- **Repository Path:** `desktop/packages/desktop_pack/capabilities/application.py`
- **Owner:** Execution Team
- **Category:** F (DUPLICATE IMPLEMENTATION)
- **Priority:** P2 (Important Feature)
- **Release Critical:** YES
- **Evidence:** `LaunchApplicationCapability` is implemented here as a mock (just logs), and correctly as an OS process spawner in `execution.py`.
- **User Impact:** If the planner routes to the mocked capability, apps will not open.
- **Architecture Impact:** Capability registry namespace collision and ambiguous dependency injection.
- **Required Action:** Delete the mock implementation in `application.py`. Canonicalize `execution.py`.

---

### ITEM 7: Production Providers Hookup
- **Feature:** Inference & Speech Providers
- **Repository Path:** `desktop/services/language/providers/mock_llm.py`, `mock_speech.py`, `desktop/services/audio/providers/mock_wake_word.py`
- **Owner:** AI Platform Team
- **Category:** C (MOCK)
- **Priority:** P0 (Blocks Release)
- **Release Critical:** YES
- **Evidence:** These mock providers supply hardcoded synthetic text/audio to bypass heavy API usage. 
- **User Impact:** Completely breaks Voice and Language capabilities in production. 
- **Architecture Impact:** Runtimes evaluating `ProviderHealth` receive fake metrics. 
- **Required Action:** Disconnect mock providers from production DI configurations. Ensure GGUF/Real providers are exclusively injected for actual releases.

---

### ITEM 8: Behavior & Character Animations
- **Feature:** Character Expression & Emotion Rendering
- **Repository Path:** `desktop/behavior/emotion_runtime.py`, `narration_runtime.py`, `expression_runtime.py`
- **Owner:** Character Platform Team
- **Category:** B (PLACEHOLDER)
- **Priority:** P1 (Critical Feature)
- **Release Critical:** YES
- **Evidence:** The source files contain interface definitions mostly populated with `pass` and `NotImplementedError`. 
- **User Impact:** CHITTI's visual avatar will not animate, show emotion, or narrate appropriately based on context.
- **Architecture Impact:** Expression Runtime fails to emit state changes to the UI renderer.
- **Required Action:** Implement the core state machines inside the behavior runtimes.
