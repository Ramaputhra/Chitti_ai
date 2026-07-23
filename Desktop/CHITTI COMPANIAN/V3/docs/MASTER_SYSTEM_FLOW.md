# CHITTI V2 — MASTER SYSTEM FLOW ARCHITECTURE
**(Single Canonical End-to-End System Graph)**

======================================================================
## 1. EXECUTIVE STATEMENT
======================================================================

This document contains the **single canonical engineering flow chart** for CHITTI V2. Every subsystem, runtime, capability, state machine, event pipeline, rendering engine, memory storage, and coordination manager is connected in **one unified flow graph**.

---

======================================================================
## 2. MASTER ARCHITECTURAL SYSTEM FLOW CHART
======================================================================

```mermaid
flowchart LR
    %% =========================================================================
    %% 00. USER & PHYSICAL OS ENTRY
    %% =========================================================================
    subgraph Physical_OS ["00. Physical Desktop & User Entry"]
        User([User Voice / Input])
        Win32OS["Windows OS / Win32 API Native Integration"]
        AudioHardware["Microphone / Speaker Hardware Interface"]
    end

    %% =========================================================================
    %% 01. BOOT, KERNEL & INFRASTRUCTURE
    %% =========================================================================
    subgraph Boot_and_Kernel ["01. BootManager, Kernel & EventBus"]
        BootManager["BootManager (Boot Sequence & Readiness Barrier)"]
        Kernel["RuntimeKernel (Lifecycle State Machine)"]
        ConfigLoader["Configuration Loader (use_llm, Hardware Profiler)"]
        EventBus{{"Deterministic EventBus (Synchronous & Async Queue)"}}
        StructuralLogger["Structural Audit Logger (JSON/Markdown Logs)"]
    end

    %% =========================================================================
    %% 02. PERCEPTION, VOICE ACTIVITY & STT ENGINE
    %% =========================================================================
    subgraph Perception_and_Speech ["02. Perception, Speech Runtime & Intent Parsing"]
        VAD["Voice Activity Detector (Audio Energy / VAD)"]
        WakeEngine["Wake Engine (Wake Word Validation)"]
        STTEngine["Speech To Text Engine (Whisper / Local Transcriber)"]
        IntentParser["Intent Parser & Entity Extractor"]
        UserIntent["Canonical UserIntent Schema"]
    end

    %% =========================================================================
    %% 03. COGNITIVE PLANNING & DECISION ENGINE
    %% =========================================================================
    subgraph Cognitive_Planning ["03. Context Assembly, Intent & Planner Runtime"]
        ContextAssembler["ContextAssembler (Read-Only State Projection)"]
        PlanningContext["PlanningContext Object"]
        ReasoningPolicy["Reasoning Policy Engine (Deterministic Filter)"]
        DecisionEngine["DecisionEngine (Rule 18 Pure - Same Context = Same Decision)"]
        PlannerRuntime["Planner Runtime (Task Graph Generator)"]
        ExecutionPlan["Immutable ExecutionPlan Schema"]
    end

    %% =========================================================================
    %% 04. WORKFLOW SPINE & EXECUTION ENGINE
    %% =========================================================================
    subgraph Execution_Spine ["04. Workflow Spine & Execution Engine"]
        WorkflowBuilder["Workflow Builder (State Machine Compiler)"]
        WorkflowRuntime["Workflow Runtime (Atomic Step Executor)"]
        ExecutionSpine["Execution Spine Manager"]
        ExecutionDelta["ExecutionDelta Event Stream"]
        ExecutionResult["ExecutionResult Schema"]
    end

    %% =========================================================================
    %% 05. CAPABILITY PLATFORM & ENVIRONMENT ADAPTERS
    %% =========================================================================
    subgraph Capability_Platform ["05. Capability Platform & Environment Adapters"]
        CapabilityRegistry["Capability Registry (Stateless Capabilities)"]
        TimeCap["Time & Distance Capability"]
        BrowserCap["Browser Automation Capability"]
        VisionCap["Vision & OCR Capability"]
        SearchCap["Knowledge Search Capability"]
        FileCap["File Automation Capability"]
        DesktopCap["Desktop Automation Capability"]
        PlaywrightAdapter["Playwright Browser Adapter"]
        Win32Adapter["Win32 Desktop Native Adapter"]
        CanonicalCapOutput["CanonicalCapabilityOutput Schema"]
    end

    %% =========================================================================
    %% 06. DESKTOP OBSERVATION & VERIFICATION ENGINE
    %% =========================================================================
    subgraph Verification_and_Observation ["06. Desktop Observation & Verification Engine"]
        DesktopObservation["Desktop Observation Engine (Process/Window/FS Captures)"]
        VerificationRuntime["Verification Runtime (Assertion Engine)"]
        PageSnapshot["PageSnapshot Schema (No Raw DOM on EventBus)"]
        VisionLayoutTree["VisionLayoutTree & Visual Bounding Boxes"]
        VerificationOutcome["VerificationOutcome (Passed / Failed / Retry)"]
    end

    %% =========================================================================
    %% 07. COGNITIVE MEMORY CORE
    %% =========================================================================
    subgraph Cognitive_Memory ["07. Episodic, Semantic Memory & Knowledge Graph"]
        MemoryAPI["MemoryAPI (Read-Only Isolation Contract)"]
        ActivityEngine["Activity Intelligence Engine (Session Tracking)"]
        EpisodicMemory["Episodic Memory Runtime"]
        SemanticMemory["Semantic Memory Runtime & Fact Validation Pipeline"]
        KnowledgeGraph["Knowledge Graph Foundation (BM25 & Vector Indexer)"]
        SQLiteDB[("SQLite Storage: chitti_memory.db")]
    end

    %% =========================================================================
    %% 08. RUNTIME SESSION BINDING
    %% =========================================================================
    subgraph Runtime_Session_Binding ["08. Runtime Session Management & State Machines"]
        SessionManager["Runtime Session Manager"]
        WidgetSessionObj["WidgetSession Model (session_id, data, active)"]
        SessionStateMachine["Session State Machine (Started, Updated, Completed)"]
    end

    %% =========================================================================
    %% 09. VISUAL COORDINATOR PLATFORM
    %% =========================================================================
    subgraph Visual_Coordinator_Platform ["09. Visual Coordinator & Priority Engine"]
        VisualCoordinator["Master Visual Coordinator Facade (Zero Rendering)"]
        TimelineScheduler["Timeline Scheduler (Unified Timeline Single Source of Truth)"]
        PriorityEngine["Priority Engine (CRITICAL > WARNING > CONVERSATION > MEDIA > IDLE)"]
        ConflictResolver["Automatic Conflict Resolver (Anchor & Layout Conflicts)"]
        VisualStateManager["Visual State Manager (Canonical Visual State: Speaking, Presenting, etc)"]
        PolicyEngine["Orchestration Policy Engine (8 Modes: Gaming, Minimal, Focus)"]
        RecoveryManager["Fault Tolerance & Crash Recovery Manager"]
        UnifiedTimeline["Unified Timeline Sequence"]
    end

    %% =========================================================================
    %% 10. CHARACTER RUNTIME & PRESENCE LIFECYCLE
    %% =========================================================================
    subgraph Character_Presence_Platform ["10. Character Runtime & Presence Lifecycle"]
        CharacterRuntime["Character Runtime (14 FPS Fixed Render Loop)"]
        PresenceController["Presence Controller (Visible, Docked, SystemTray)"]
        BehaviorScheduler["Behavior Scheduler (Timeline Builder & Sequence Manager)"]
        MotionDesignSystem["Motion Design System (Spring Tokens & Slime 5% Stretch Limit)"]
        HotkeyListener["Global Hotkey Listener"]
        SystemTrayManager["System Tray Manager"]
        CharacterAnchorAPI["Character Anchor API (get_character_anchor)"]
    end

    %% =========================================================================
    %% 11. TTS ENGINE & SPEECH TIMELINE
    %% =========================================================================
    subgraph Voice_and_Speech_Timeline ["11. TTS Engine, Speech Timeline & Lipsync"]
        VoiceRuntime["Voice & Speech Runtime Facade"]
        TTSEngine["TTS Engine (Voice Synthesis & Audio Buffer)"]
        SpeechTimeline["Speech Timeline (Sentence Boundaries & Audio Duration)"]
        LipsyncGenerator["Lipsync Marker Generator"]
        CharacterIdentity["Character Identity Platform (display_name: CHITTI)"]
        PersonalityEngine["Personality Engine (Emotion State & Narration Rules)"]
    end

    %% =========================================================================
    %% 12. DESKTOP UI RUNTIME FOUNDATION
    %% =========================================================================
    subgraph Desktop_UI_Runtime ["12. Desktop UI Runtime Foundation & Window System"]
        DesktopUIRuntime["Desktop UI Runtime Facade (Zero Character PNG Decoding)"]
        WindowManager["Master Window Manager"]
        WindowRegistry["Window Registry & Z-Order Manager"]
        CanonicalWindowIDs["Canonical Window IDs (window_id.py)"]
        SemanticLayers["Semantic Window Layers (CHARACTER < DIALOG < OVERLAY)"]
        WindowAttachmentAPI["Generic Window Attachment API (WindowAttachment.py)"]
        TransparentWindow["TransparentWindow Base (Frameless, Per-Pixel Alpha)"]
        MasterUIRenderer["Master UI Renderer (GPU Hardware Accelerated Composition)"]
        RenderProfiles["Render Profiles (Widget 30 FPS, Waveform 24 FPS, Static Event-Driven)"]
        TextureCache["GPU Texture Cache & Asset Cache"]
        ThemeManager["Theme Manager (Dark, Light, System)"]
    end

    %% =========================================================================
    %% 13. DESKTOP WIDGET FRAMEWORK
    %% =========================================================================
    subgraph Desktop_Widget_Framework ["13. Desktop Widget Framework & 17 Generic Widgets"]
        WidgetRuntime["Master Widget Runtime Facade"]
        WidgetManager["Widget Manager (Lazy Instantiation & No Window Ownership)"]
        WidgetSDK["Widget SDK (BaseWidget, WidgetContext, WidgetTheme 10px Radius)"]
        WidgetRegistry["Widget Registry (Category Filtering & Version Validation)"]
        WidgetManifestLoader["Widget Manifest Loader (JSON Schema v1.0.0 & Hot Reload)"]
        GenericWidgets["17 Generic Widgets (Media, Reminder, Email, Browser, Vision, System, etc)"]
        MockSessionProvider["Mock Session Provider & Preview Studio"]
    end

    %% =========================================================================
    %% 14. PRESENTATION RUNTIME
    %% =========================================================================
    subgraph Presentation_Runtime ["14. Presentation Engine, Experiences & Recipes"]
        PresentationEngine["Presentation Engine & Session Runtime"]
        SlideDeck["Slide Deck Renderer & Laser Pointer Tracker"]
        ExperienceLibrary["Presentation Experience Library & Replay API"]
    end

    %% =========================================================================
    %% 15. TELEMETRY, ANALYTICS & AUDIT
    %% =========================================================================
    subgraph Analytics_and_Audit ["15. Telemetry, Analytics & Structural Logging"]
        AnalyticsPublisher["Analytics Publisher (Non-Content Metric Telemetry)"]
        MetricsTracker["Performance Metrics Tracker"]
    end

    %% =========================================================================
    %% 16. PLUGIN MANAGER & DEVELOPER TOOLS
    %% =========================================================================
    subgraph Plugin_and_DevTools ["16. Plugin Manager, Settings & Developer Tools"]
        PluginCoordinator["Plugin Coordinator (Plugin Orchestration Hooks)"]
        DebugTimeline["Debug Timeline Inspector & Visual Event Viewer"]
        VerificationMonitor["Verification Monitor (Invariant Enforcer)"]
    end

    %% =========================================================================
    %% END-TO-END PIPELINE CONNECTIONS (ONE SINGLE FLOW)
    %% =========================================================================

    %% 1. Startup & Kernel Wiring
    BootManager -->|01. Initialize| ConfigLoader
    ConfigLoader -->|02. Load Config| Kernel
    Kernel -->|03. Instantiate| EventBus
    Kernel -->|04. Register Runtimes| CapabilityRegistry
    Kernel -->|05. Boot Ack| EventBus

    %% 2. Audio Capture to Intent Parser
    User -->|06. Speaks Audio| AudioHardware
    AudioHardware -->|07. Raw Stream| VAD
    VAD -->|08. Audio Frames| WakeEngine
    WakeEngine -->|09. Validated Wake| STTEngine
    STTEngine -->|10. Transcribed Text| IntentParser
    IntentParser -->|11. Produce| UserIntent
    UserIntent -->|12. Dispatch Intent| EventBus

    %% 3. Context & Planning Pipeline
    EventBus -->|13. Receive Intent| ContextAssembler
    Win32OS -.->|14. Desktop State| ContextAssembler
    MemoryAPI -.->|15. Retrieve Context| ContextAssembler
    ContextAssembler -->|16. Build| PlanningContext
    PlanningContext -->|17. Filter| ReasoningPolicy
    ReasoningPolicy -->|18. Pure Evaluation| DecisionEngine
    DecisionEngine -->|19. Generate Graph| PlannerRuntime
    PlannerRuntime -->|20. Produce| ExecutionPlan

    %% 4. Workflow Spine Execution
    ExecutionPlan -->|21. Compile State Machine| WorkflowBuilder
    WorkflowBuilder -->|22. Execute Plan| WorkflowRuntime
    WorkflowRuntime -->|23. Coordinate| ExecutionSpine
    ExecutionSpine -->|24. Emit Steps| ExecutionDelta
    ExecutionDelta -->|25. Request Invocation| CapabilityRegistry

    %% 5. Capability Execution & Adapters
    CapabilityRegistry --> TimeCap
    CapabilityRegistry --> BrowserCap
    CapabilityRegistry --> VisionCap
    CapabilityRegistry --> SearchCap
    CapabilityRegistry --> FileCap
    CapabilityRegistry --> DesktopCap

    BrowserCap -->|26. Automate| PlaywrightAdapter
    DesktopCap -->|27. Automate| Win32Adapter
    PlaywrightAdapter --> Win32OS
    Win32Adapter --> Win32OS

    TimeCap --> CanonicalCapOutput
    BrowserCap --> CanonicalCapOutput
    VisionCap --> CanonicalCapOutput
    SearchCap --> CanonicalCapOutput
    FileCap --> CanonicalCapOutput
    DesktopCap --> CanonicalCapOutput
    CanonicalCapOutput -->|28. Output Delta| ExecutionResult

    %% 6. Observation & Verification
    ExecutionResult -->|29. Trigger Snapshot| DesktopObservation
    Win32OS -.->|30. Capture Layout/Process| DesktopObservation
    DesktopObservation --> PageSnapshot
    DesktopObservation --> VisionLayoutTree
    PageSnapshot --> VerificationRuntime
    VisionLayoutTree --> VerificationRuntime
    VerificationRuntime -->|31. Evaluate Assertions| VerificationOutcome
    VerificationOutcome -->|32. Pass Event| EventBus

    %% 7. Memory & Activity Recording
    Win32OS -.->|33. Raw OS Activity| ActivityEngine
    ActivityEngine -->|34. Log Session| EpisodicMemory
    EpisodicMemory -->|35. Persist Episode| SQLiteDB
    SQLiteDB --> SemanticMemory
    SemanticMemory --> KnowledgeGraph
    KnowledgeGraph --> MemoryAPI

    %% 8. Runtime Session Binding
    EventBus -->|36. Session Started| SessionManager
    SessionManager --> SessionStateMachine
    SessionStateMachine --> WidgetSessionObj

    %% 9. Visual Coordinator Orchestration
    WidgetSessionObj -->|37. Notify Session| VisualCoordinator
    VisualCoordinator --> TimelineScheduler
    VisualCoordinator --> PriorityEngine
    VisualCoordinator --> ConflictResolver
    VisualCoordinator --> VisualStateManager
    VisualCoordinator --> PolicyEngine
    VisualCoordinator --> RecoveryManager
    TimelineScheduler --> UnifiedTimeline

    %% 10. Voice & TTS Generation
    VisualCoordinator -->|38. Trigger Narration| VoiceRuntime
    VoiceRuntime --> CharacterIdentity
    VoiceRuntime --> PersonalityEngine
    PersonalityEngine --> TTSEngine
    TTSEngine --> SpeechTimeline
    TTSEngine --> LipsyncGenerator
    TTSEngine -->|39. Audio Buffer| AudioHardware

    %% 11. Character Runtime & Presence
    VisualCoordinator -->|40. Schedule Animation| CharacterRuntime
    CharacterRuntime --> PresenceController
    PresenceController --> HotkeyListener
    PresenceController --> SystemTrayManager
    BehaviorScheduler --> MotionDesignSystem
    MotionDesignSystem --> CharacterRuntime
    CharacterRuntime --> CharacterAnchorAPI
    CharacterRuntime -->|41. Render 14 FPS Slime| Win32OS

    %% 12. Desktop UI Runtime Foundation
    VisualCoordinator -->|42. Position Windows| DesktopUIRuntime
    DesktopUIRuntime --> WindowManager
    WindowManager --> WindowRegistry
    WindowManager --> CanonicalWindowIDs
    WindowManager --> SemanticLayers
    WindowManager --> TransparentWindow
    TransparentWindow --> WindowAttachmentAPI
    CharacterAnchorAPI -.->|43. Read Anchor Only| WindowAttachmentAPI
    TransparentWindow --> MasterUIRenderer
    MasterUIRenderer --> RenderProfiles
    MasterUIRenderer --> TextureCache
    ThemeManager --> MasterUIRenderer
    MasterUIRenderer -->|44. GPU Composition| Win32OS

    %% 13. Desktop Widget Framework
    WidgetSessionObj -->|45. Bind Data| WidgetRuntime
    WidgetRuntime --> WidgetManager
    WidgetManager --> WidgetSDK
    WidgetManager --> WidgetRegistry
    WidgetRegistry --> WidgetManifestLoader
    WidgetSDK --> GenericWidgets
    GenericWidgets -->|46. Request Generic Window| DesktopUIRuntime
    WidgetSDK --> WindowAttachmentAPI

    %% 14. Presentation Runtime
    VisualCoordinator -->|47. Sync Slides| PresentationEngine
    PresentationEngine --> SlideDeck
    PresentationEngine --> ExperienceLibrary
    SlideDeck --> DesktopUIRuntime

    %% 15. Analytics & Audit Logging
    EventBus -->|48. Dispatch Events| StructuralLogger
    EventBus -->|49. Telemetry Events| AnalyticsPublisher
    AnalyticsPublisher --> MetricsTracker

    %% 16. Plugin & DevTools Monitoring
    EventBus -->|50. Monitor Invariants| VerificationMonitor
    EventBus -->|51. Inspect Timeline| DebugTimeline
    PluginCoordinator -->|52. Register Hooks| VisualCoordinator
```

---

======================================================================
## 3. ARCHITECTURAL BOUNDARY & INVARIANT AUDIT
======================================================================

1. **Single Master Graph Constraint:** This document contains **EXACTLY ONE** Mermaid diagram representing the complete end-to-end architecture and data flow.
2. **Rule 18 DecisionEngine Purity:** `DecisionEngine` consumes read-only `PlanningContext` and outputs deterministic `ExecutionPlan` with zero side effects.
3. **Character Platform Isolation:** Desktop UI Runtime and Widget Framework consume ONLY `get_character_anchor()` API. They NEVER move the Character Window or decode Character PNG assets.
4. **Visual Coordinator Decoupling:** `VisualCoordinator` coordinates timing, priority, and session lifecycle without performing UI rendering or capability execution.
5. **Memory Hierarchy:** Reads occur via `MemoryAPI`; writes strictly occur via episodic logging (`PersistEpisode`) into SQLite `chitti_memory.db`.
