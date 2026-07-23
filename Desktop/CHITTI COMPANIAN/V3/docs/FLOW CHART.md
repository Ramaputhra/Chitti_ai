# 1. Complete Repository Architecture

```mermaid
flowchart TD
Root["desktop/"]
Root --> Brain["brain/"]
Brain --> Intelligence["intelligence/"]
Brain --> Reasoning["reasoning/"]
Brain --> Decision["decision/"]
Brain --> Planning["planning/"]
Brain --> Execution["execution/"]
Brain --> Memory["memory/"]
Brain --> Graph["graph/"]
Brain --> Consolidation["consolidation/"]

Root --> Bootstrap["bootstrap/"]
Bootstrap --> Config["config.py"]
Bootstrap --> Container["container.py"]
Bootstrap --> Lifecycle["lifecycle.py"]
Bootstrap --> Manager["manager.py"]

Root --> Orchestrator["orchestrator/"]
Orchestrator --> CognitivePipeline["cognitive_pipeline.py"]
Orchestrator --> Feedback["feedback.py"]

Root --> Observability["observability/"]
Observability --> ObsManager["manager.py"]
Observability --> Logger["logger.py"]
Observability --> Metrics["metrics.py"]
Observability --> Tracer["tracer.py"]
Observability --> Diagnostics["diagnostics.py"]

Root --> Updater["updater/"]
Updater --> UpdManager["manager.py"]
Updater --> Rollback["rollback.py"]
Updater --> InstallHooks["installer_hooks.py"]

DeployRoot["deploy/"]
DeployRoot --> Spec["chitti_v2.spec"]
DeployRoot --> Iss["installer.iss"]
DeployRoot --> Assets["assets/"]

Main["main.py"]
```

# 2. Repository Ownership

```mermaid
flowchart TD
EE6["EE6: Bootstrap Runtime"] --> Bootstrap["desktop/bootstrap/"]
EE1_EE4["EE1-EE4: Cognitive Runtime Integrations"] --> Orchestrator["desktop/orchestrator/"]
EE7["EE7: Observability Runtime"] --> Observability["desktop/observability/"]
EE8["EE8: Deployment & Updater"] --> Updater["desktop/updater/"]
EE8 --> Deploy["deploy/"]
S31["Sprints 31A-31I: Cognitive Spine"] --> Brain["desktop/brain/"]
```

# 3. Startup Flow

```mermaid
flowchart TD
Main["main.py"] --> BootstrapManager["BootstrapManager"]
BootstrapManager --> ConfigLoader["ConfigurationLoader.load()"]
ConfigLoader --> DependencyContainer["DependencyContainer"]
DependencyContainer --> Registry["ServiceRegistry"]
Registry --> ObservabilityManager["ObservabilityManager (Lazy Load)"]
Registry --> LifecycleManager["LifecycleManager"]
LifecycleManager --> Orchestrator["MainOrchestrator"]
Orchestrator --> Ready["System Ready"]
```

# 4. Dependency Injection Graph

```mermaid
flowchart TD
Container["DependencyContainer"] --> Registry["ServiceRegistry"]
Registry --> Services["Registered Services"]
Services --> ObsService["ObservabilityManager"]
Services --> LfService["LifecycleManager"]
Services --> CogService["CognitivePipeline"]
```

# 5. Runtime Service Graph

```mermaid
flowchart TD
Bootstrap["BootstrapManager"] --> DependencyContainer["DependencyContainer"]
DependencyContainer --> ObsManager["ObservabilityManager"]
DependencyContainer --> LfManager["LifecycleManager"]
DependencyContainer --> Orchestrator["MainOrchestrator"]
Orchestrator --> CogPipeline["CognitivePipeline"]
```

# 6. Audio Pipeline

```mermaid
flowchart TD
Mic["Microphone"] --> AudioThread["AudioThread"]
AudioThread --> WakeWord["WakeWord Engine"]
WakeWord --> SpeechCapture["Speech Capture"]
SpeechCapture --> STT["STT Engine"]
STT --> Transcript["Transcript"]
```

# 7. Wakeword Pipeline

```mermaid
flowchart TD
AudioStream["Audio Stream"] --> VAD["VAD"]
VAD --> WakewordModel["Wakeword Model"]
WakewordModel --> Trigger["Wake Trigger"]
```

# 8. STT Pipeline

```mermaid
flowchart TD
SpeechCapture["Speech Buffer"] --> Preprocess["Preprocess Audio"]
Preprocess --> STTModel["STT Model"]
STTModel --> Postprocess["Postprocess Text"]
Postprocess --> Transcript["Transcript"]
```

# 9. Conversation Pipeline

```mermaid
flowchart TD
Transcript["Transcript"] --> InteractionSession["InteractionSession"]
InteractionSession --> InputAdapter["InputAdapter"]
InputAdapter --> ExperienceObject["Experience Object"]
```

# 10. Cognitive Pipeline

```mermaid
flowchart TD
Experience["Experience"] --> S31A["Memory Builder (31A)"]
S31A --> S31B["Memory Compiler (31B)"]
S31B --> S31C["Knowledge Graph (31C)"]
S31C --> S31D["Intelligence Layer (31D)"]
S31D --> S31E["Learning (31E)"]
S31E --> S31F["Reasoning (31F)"]
S31F --> S31G["Decision (31G)"]
S31G --> S31H["Planning (31H)"]
S31H --> S31I["Execution (31I)"]
S31I --> ExecutionResult["Execution Result"]
```

# 11. Memory Architecture

```mermaid
flowchart TD
ExperienceBuilder["Experience Builder"] --> MemoryCompiler["Memory Compiler"]
MemoryCompiler --> Episodic["Episodic Storage"]
MemoryCompiler --> Semantic["Semantic Storage"]
Episodic --> SQLite["chitti_memory.db"]
Semantic --> SQLite
```

# 12. Knowledge Graph

```mermaid
flowchart TD
MemoryCompiler["Memory Compiler"] --> EntityExtraction["Entity Extraction"]
EntityExtraction --> RelationshipBuilder["Relationship Builder"]
RelationshipBuilder --> GraphStorage["Graph DB (SQLite)"]
GraphStorage --> GraphQuery["Graph Query Interface"]
```

# 13. Intelligence Layer

```mermaid
flowchart TD
GraphQuery["Graph Query"] --> ContextAssembly["Context Assembly"]
EpisodicQuery["Episodic Query"] --> ContextAssembly
ContextAssembly --> IntelligentContext["Intelligent Context"]
```

# 14. Reasoning Layer

```mermaid
flowchart TD
IntelligentContext["Intelligent Context"] --> PatternMatcher["Pattern Matcher"]
PatternMatcher --> InferenceEngine["Inference Engine"]
InferenceEngine --> DerivedInsights["Derived Insights"]
```

# 15. Decision Layer

```mermaid
flowchart TD
DerivedInsights["Derived Insights"] --> IntentResolver["Intent Resolver"]
IntentResolver --> PolicyValidator["Policy Validator"]
PolicyValidator --> ActionIntent["Action Intent"]
```

# 16. Planning Layer

```mermaid
flowchart TD
ActionIntent["Action Intent"] --> GoalDecomposer["Goal Decomposer"]
GoalDecomposer --> StepGenerator["Step Generator"]
StepGenerator --> ExecutionPlan["Execution Plan"]
```

# 17. Execution Layer

```mermaid
flowchart TD
ExecutionPlan["Execution Plan"] --> CapabilityRouter["Capability Router"]
CapabilityRouter --> CapabilityBinder["Capability Binder"]
CapabilityBinder --> ExecutionEngine["Execution Engine"]
ExecutionEngine --> ExecutionResult["Execution Result"]
```

# 18. Capability Platform

```mermaid
flowchart TD
CapabilityRegistry["CapabilityRegistry"] --> OS["OS Integration"]
CapabilityRegistry --> Browser["Browser Automation"]
CapabilityRegistry --> FS["File System"]
ExecutionEngine["Execution Engine"] --> CapabilityRegistry
OS --> ExecutionResult["Execution Result"]
Browser --> ExecutionResult
FS --> ExecutionResult
```

# 19. Vision Pipeline

```mermaid
flowchart TD
ScreenCapture["Screen Capture"] --> OCR["OCR"]
ScreenCapture --> ObjectDetection["Object Detection"]
OCR --> VisionIntelligence["Vision Intelligence"]
ObjectDetection --> VisionIntelligence
VisionIntelligence --> MergedContext["Merged Context"]
```

# 20. Character Layer

```mermaid
flowchart TD
ExecutionResult["Execution Result"] --> EmotionModel["Emotion Model"]
EmotionModel --> ToneGenerator["Tone Generator"]
ToneGenerator --> CharacterPrompt["Character Prompt"]
```

# 21. LLM Pipeline

```mermaid
flowchart TD
CharacterPrompt["Character Prompt"] --> LLMModel["LLM Engine"]
LLMModel --> TextStream["Text Stream"]
```

# 22. Response Generation

```mermaid
flowchart TD
TextStream["Text Stream"] --> PostProcessor["Post Processor"]
PostProcessor --> FinalResponse["Final Response"]
```

# 23. TTS Pipeline

```mermaid
flowchart TD
FinalResponse["Final Response"] --> TTSEngine["TTS Engine"]
TTSEngine --> AudioRenderer["Audio Renderer"]
AudioRenderer --> Speaker["Speaker"]
```

# 24. UI Pipeline

```mermaid
flowchart TD
FinalResponse["Final Response"] --> DesktopUI["Desktop UI"]
DesktopUI --> Overlay["Screen Overlay"]
DesktopUI --> Widget["Widgets"]
```

# 25. Continuous Learning

```mermaid
flowchart TD
ExecutionResult["ExecutionResult"] --> FeedbackCollector["FeedbackCollector"]
FeedbackCollector --> ExperienceBuilder["ExperienceBuilder"]
ExperienceBuilder --> ConsolidationEngine["ConsolidationEngine"]
ConsolidationEngine --> SQLite["SQLite Memory"]
```

# 26. Observability

```mermaid
flowchart TD
Runtime["Any Runtime Component"] --> ObsManager["ObservabilityManager"]
ObsManager --> WorkerThread["TelemetryWorkerThread"]
WorkerThread --> StructuredLogger["StructuredLogger"]
WorkerThread --> MetricsRegistry["MetricsRegistry"]
WorkerThread --> ExecutionTracer["ExecutionTracer"]
StructuredLogger --> Diagnostics["DiagnosticSnapshotGenerator"]
```

# 27. Bootstrap

```mermaid
flowchart TD
ConfigLoader["ConfigurationLoader"] --> DepContainer["DependencyContainer"]
DepContainer --> LifecycleManager["LifecycleManager"]
LifecycleManager --> BootPhase1["Phase 1 Init"]
LifecycleManager --> BootPhase2["Phase 2 Init"]
LifecycleManager --> Running["Running State"]
```

# 28. Deployment

```mermaid
flowchart TD
Installer["Installer (.exe)"] --> InstallHooks["InstallationManager"]
InstallHooks --> AssetManifest["AssetManifest Validation"]
AssetManifest --> ConfigProvision["Configuration Provisioning"]
ConfigProvision --> Runtime["Runtime"]
UpdateManager["UpdateManager"] --> UpdateManifest["UpdateManifest"]
UpdateManifest --> Staging["Staging Payload"]
Staging --> Rollback["RollbackManager"]
Rollback --> Runtime
```

# 29. Thread Architecture

```mermaid
flowchart TD
MainThread["Main Thread (Lifecycle, Config, UI)"]
AudioThread["Audio Thread (Mic, Wakeword)"]
TelemetryThread["TelemetryWorkerThread (Queue Consumer)"]
UpdateThread["UpdateManager Polling Thread"]
ExecutionThread["Cognitive Pipeline Thread (Async)"]

MainThread --> AudioThread
MainThread --> TelemetryThread
MainThread --> UpdateThread
MainThread --> ExecutionThread
```

# 30. Database Architecture

```mermaid
flowchart TD
SQLite["SQLite Engine"]
SQLite --> MemoryDB["chitti_memory.db"]
MemoryDB --> EpisodicTables["Episodic Tables"]
MemoryDB --> SemanticTables["Semantic Tables"]
MemoryDB --> GraphTables["Graph Tables"]
```

# 31. End-to-End Request Flow

```mermaid
flowchart TD
UserSpeak["User Speaks"] --> STT["STT"]
STT --> Transcript["Transcript"]
Transcript --> CognitivePipeline["CognitivePipeline (31A-31I)"]
CognitivePipeline --> ExecutionResult["ExecutionResult"]
```

# 32. End-to-End Response Flow

```mermaid
flowchart TD
ExecutionResult["ExecutionResult"] --> CharacterLayer["Character Layer"]
CharacterLayer --> LLM["LLM"]
LLM --> TTS["TTS"]
TTS --> AudioRenderer["Audio Renderer"]
AudioRenderer --> UserHear["User Hears Response"]
```

# 33. Complete CHITTI V2 Master Architecture

```mermaid
flowchart TD
    User["User"] --> Microphone["Microphone"]
    Microphone --> AudioPipeline["Audio Pipeline"]
    AudioPipeline --> Transcript["Transcript"]
    
    Transcript --> InputAdapter["InputAdapter"]
    InputAdapter --> ExperienceObj["Experience Object"]
    
    ExperienceObj --> S31A["Memory Builder (31A)"]
    S31A --> S31B["Memory Compiler (31B)"]
    S31B --> S31C["Knowledge Graph (31C)"]
    S31C --> S31D["Intelligence Layer (31D)"]
    S31D --> S31E["Learning (31E)"]
    S31E --> S31F["Reasoning (31F)"]
    S31F --> S31G["Decision (31G)"]
    S31G --> S31H["Planning (31H)"]
    S31H --> S31I["Execution (31I)"]
    
    S31I --> CapabilityRegistry["CapabilityRegistry"]
    CapabilityRegistry --> ExecResult["ExecutionResult"]
    
    ExecResult --> FeedbackCollector["FeedbackCollector"]
    FeedbackCollector --> S31A
    
    ExecResult --> CharacterLayer["Character Layer"]
    CharacterLayer --> LLM["LLM"]
    LLM --> TTS["TTS"]
    TTS --> User
    
    BootstrapManager["BootstrapManager"] --> MainOrchestrator["MainOrchestrator"]
    MainOrchestrator --> ExperienceObj
    
    ObservabilityManager["ObservabilityManager"] --> TelemetryWorkerThread["TelemetryWorkerThread"]
    TelemetryWorkerThread --> StructuredLogger["StructuredLogger"]
    TelemetryWorkerThread --> MetricsRegistry["MetricsRegistry"]
    TelemetryWorkerThread --> ExecutionTracer["ExecutionTracer"]
    
    InstallationManager["InstallationManager"] --> AssetManifest["AssetManifest"]
    AssetManifest --> ConfigurationLoader["ConfigurationLoader"]
    ConfigurationLoader --> BootstrapManager
    
    UpdateManager["UpdateManager"] --> UpdateManifest["UpdateManifest"]
    UpdateManifest --> RollbackManager["RollbackManager"]
    RollbackManager --> ConfigurationLoader
    
    S31A --> MemoryDB["chitti_memory.db"]
    S31C --> MemoryDB
```
