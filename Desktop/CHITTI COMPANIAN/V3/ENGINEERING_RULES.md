# Engineering Rules

## Engineering Philosophy

**Rule 1**: Never duplicate business logic.
**Rule 2**: Every capability is testable.
**Rule 3**: Planner never performs execution.
**Rule 4**: Capabilities never speak directly.
**Rule 5**: Runtime owns execution.
**Rule 6**: User always confirms destructive actions.
**Rule 7**: Archive > Delete.
**Rule 8**: Experience before Infrastructure.

---

## Architectural Rules

The following rules dictate the architectural patterns and code quality expectations for the entire CHITTI project.

## 1. Interface-First Design
Every major component must be defined by an `I[Name]` interface in `desktop/core/interfaces/` before its concrete implementation is built in `desktop/services/`.

## 2. Dependency Injection
Use the `DIContainer` established in the Composition Root (`desktop/app.py`). Services must never directly instantiate their dependencies.

## 3. Event-Driven Communication
Cross-module communication must use the `IEventBus`. Do not create direct object references between domains (e.g., Audio must not directly call Language Runtime). Use formal `SystemEvents`.

## 4. Single Source of Truth
The `IStateManager` holds all global runtime state, while `ICapabilityRegistry` maintains feature readiness. Avoid local state hoarding in services.

## 5. Conversation Context
**Every externally observable interaction must occur inside a ConversationSession.** 
Whether initiated by Voice, a Desktop Shortcut, an API call, or a Robot Sensor, it MUST be wrapped in a `ConversationSession` via the `ConversationManager` to guarantee traceability, lifecycle management, and logging.

## 6. Local-First Operation
**All core voice functionality must operate fully offline.** 
Cloud providers may enhance capability (e.g., via LLMs or premium TTS) but must never be required for basic operation (Wake Word, STT, core TTS, and desktop control).

## 7. Universal Provider Pattern
Every external dependency must follow the exact same architectural pattern:
`Interface -> Router -> Provider Registry -> Provider Implementation`.
This guarantees CHITTI can swap models/providers without structural rewrites.

## 8. LLM Tool Execution
**LLM providers must never execute tools directly.**
Instead, the LLM must emit a structured intent which is passed to the Planner -> Workflow -> Tool Manager -> Execution. This prevents provider-specific function-calling APIs from leaking into the core architecture and ensures models remain interchangeable.

## 9. Capability Isolation
**Operating Capabilities must never call other Operating Capabilities directly.**
All cross-capability workflows must return to the Planner/Executor for orchestration. This keeps the architecture acyclic and ensures orchestration always remains visible to the planner and telemetry systems.

## 10. Artifact Exchange
**Capabilities must exchange Artifacts, never provider-specific objects or raw strings.**
All tools must output structured `Artifact` models (e.g., `DocumentArtifact`, `EmailArtifact`) wrapped in an `ExecutionResult`. This establishes a universal language across the platform and creates the foundation for the Knowledge and Memory runtimes.

## 11. Fact vs Significance Separation
**Knowledge Runtime owns facts. Memory Runtime owns significance.**
The Knowledge Graph stores immutable artifacts, entities, and objective relationships. The Memory Runtime stores subjective meaning, importance, preferences, and long-term context derived from that knowledge.

## 12. Semantic Enrichment Independence
**Semantic Runtime may enrich Knowledge, but it may never modify or overwrite immutable Artifacts.**
Artifacts stay immutable forever. Entity Extraction, Canonicalization, and Alias Resolution enrich the Knowledge Graph by generating new `Entities` and `KnowledgeEdges`, never by mutating the source `Artifacts`.

## 13. Perception Boundary Rule
**Perception providers may only publish Artifacts and AttentionEvents. They must never directly invoke Planning, Knowledge, Memory, or Execution services.**

## 14. Perception Aggregation Rule
**Every Capability Runtime must first construct a domain-specific Model (e.g., `SceneModel`, `ScreenModel`, `RobotModel`) before generating `PerceptionArtifacts` or `AttentionEvents`. Provider outputs must never bypass the model aggregation layer.**

## 15. Hardware Execution Isolation Rule
**Robot providers may publish only `RobotArtifacts`, `PerceptionArtifacts`, and `AttentionEvents`. Robot outputs must be executed exclusively through the `Expression Runtime` using `RobotCommand`s. Sensor providers must never directly actuate hardware.**

## 16. Unified Actuation Rule
**All hardware outputs must flow exclusively through the `Expression Runtime`. The Planner, Execution Runtime, Capabilities, and Providers must never directly control servos, LEDs, displays, speakers, or other actuators. Every physical action must be represented as an `ExpressionModel` and executed through an `ExpressionProvider`.**

## 17. Deterministic Actuation Rule
**Expression Providers may execute only scheduled `ExpressionSequence`s generated by the `Expression Runtime`. Providers must never interpret intent, generate behaviors, or communicate directly with the Planner.**

## 18. Local-First Intelligence Rule
**All core AI capabilities (speech, language, vision, OCR, embeddings, retrieval) must operate using open-weight, self-hostable models.** Cloud providers are optional extensions that implement the same provider contracts and are disabled by default. No core workflow may require Internet connectivity.

## 19. Capability-Based AI Selection
**The Planner must never request a specific AI model.** It requests an AI capability (reasoning, coding, OCR, vision, speech, embedding, reranking, translation). Model selection is the exclusive responsibility of the AI Orchestrator using the Model Registry.

## 20. AI Pipeline Composition
**Multi-stage AI workflows must be represented as immutable `AIExecutionStrategy` objects.** The Planner specifies the desired capability and outcome, but it must never manually chain individual AI models or providers. Composition, scheduling, retries, and fallback are the exclusive responsibility of the AI Orchestrator.

## 21. Live Demonstration
**Every sprint must end with a live demonstration.** The primary output of a sprint is a working user experience, not just merged code.

## 34. Presence Subscribers
**Components that react to presence (UI, audio, hardware, lighting, haptics, telemetry, etc.) must subscribe to `PresenceStateChanged` events independently.** The `PresenceEngine` publishes state transitions but must never orchestrate or directly invoke individual subscribers.

## 35. Subscriber Isolation
**Subscribers to `PresenceStateChanged` must operate independently.** A failure, timeout, or exception in one subscriber must never prevent delivery of the event to other subscribers. Event dispatch must isolate subscriber failures and continue processing remaining listeners.

## 36. Presence is Declarative
**Presence describes what CHITTI is doing, never how it is expressed.** States must represent declarative phases of execution (e.g. `LISTENING`, `THINKING`, `WORKING`). They must never define physical or UI mechanisms (e.g. `PLAY_BLUSH`, `NOD_HEAD`). Translating declarative state into expression is the exclusive responsibility of the Expression Runtime.

## 37. Expression Runtime Coordination
**The Expression Runtime determines what expression should occur and when.** Individual output runtimes (visual, audio, servo, lighting, haptics, etc.) determine *how* that expression is rendered on their respective medium. The Expression Runtime must never manipulate output implementations directly.

## 38. Declarative Expression Assets
**Expression manifests describe desired outputs using symbolic asset identifiers** (animation IDs, motion IDs, sound IDs, etc.). Runtime code must never embed file paths, servo angles, or device-specific parameters.

## 41. Cooperative Cancellation
**Workflow cancellation must be cooperative.** Runtimes signal cancellation through a `CancellationToken`; capabilities are responsible for terminating safely at defined cancellation points. The runtime must never forcibly terminate capability execution except during application shutdown.

## 42. Capability Purity
**Capabilities execute exactly one invocation and return exactly one `ExecutionResult`.** They must not implement retries, workflow sequencing, timeout logic, or compensation behavior.

## Rule 96 – Inference Isolation
The Inference Runtime is responsible only for generating responses from conversational context. It must not execute tools, manipulate UI, invoke hardware, or alter application state beyond publishing inference events.

## Rule 98 — Capability Contracts
Capabilities communicate exclusively through structured `ExecutionResult` objects. Human-readable responses, personality, and localization must be handled outside the capability implementation.

## Rule 99 – Verified Response Generation
Conversational responses about desktop actions must be generated only from verified execution results. Language models must never claim an action succeeded based solely on capability output. The Conversation Runtime is responsible for supplying structured, verified evidence before requesting a spoken response.

## Rule 100 – Learn Only Verified Experiences
Only workflows that have completed successfully and passed evidence verification may become learning candidates. An experience should be promoted to the deterministic experience library only after repeated verified success (e.g., 3 consecutive successes).

## Rule 101 – Adaptive Confidence
Learned experiences are not permanent truths. Confidence must increase after verified success and decrease after verified failure. Experiences whose confidence falls below the acceptance threshold should automatically return to probabilistic planning until revalidated.

## Rule 102 – Built-in Before Learned Before Planned
Request resolution must always follow this deterministic order:
1. Built-in deterministic intents.
2. Stable learned experiences.
3. Probabilistic LLM planning.
New knowledge should reduce dependence on higher-cost planning over time, never increase it.

## Rule 104 – Conversation as the Source of Truth
Conversation sessions are the canonical representation of user interaction. Voice input, typed input, capability execution, inference, verification, and presentation must attach to a conversation session and turn. UI components must observe conversation events rather than own conversational state.

## Rule 239 – Intent Runtime Interpretive Boundary
The Intent Runtime is the final component permitted to interpret natural language. Every runtime after the Intent Runtime operates exclusively on structured data and canonical intents, and must never parse or infer meaning from raw human language directly.

## Rule 240 – Orchestration Boundaries
Workflow describes what should happen. Planner determines how it should be prepared. Execution Graph describes task dependencies. Scheduler determines when work runs. Execution Runtime performs the work.

## Rule 241 – Workflow Instance Immutability
Workflow Templates are immutable definitions. Workflow Instances are mutable runtime objects. Planner, Scheduler, and Execution Runtime must operate only on Workflow Instances. Templates must never be modified during execution.

## Rule 242 – Orchestration Communication Boundary
Workflow Runtime, Planner Runtime, Execution Graph Runtime, Scheduler Runtime, and Execution Runtime must never directly invoke one another. Communication between orchestration stages shall occur exclusively through immutable events and runtime-owned data contracts.

## Rule 243 — Constructor Injection Only
Runtimes shall receive dependencies exclusively through constructor injection. Service locators, global singletons, and runtime-owned dependency creation are prohibited.

## Rule 241 — Communication Session Origin
Every user interaction shall originate from exactly one Communication Session. No runtime may infer or create user interactions outside an active session except notifications explicitly initiated by CHITTI.

## Rule 14 — Audio Runtime Identity Constraint
The Audio Runtime identifies speakers but never authenticates users. Authentication decisions belong exclusively to the Policy Runtime.the EventBus.

## Rule 245 — Configuration Isolation
Runtime modules shall never access configuration files directly. All configuration must be supplied through the Configuration Manager.

## Rule 246 — Context Propagation
Workflow, session, authentication, and conversation context shall be propagated automatically by the infrastructure. Business runtimes must never manually construct or mutate shared execution context.

## Rule 247 — Event Immutability
Once an event enters the EventBus, it shall never be modified. Infrastructure components may wrap or enrich events by producing a new immutable event object or attaching external context using an Event Envelope, but the original event payload must remain unchanged.

## Rule 248 — Infrastructure Isolation
Infrastructure components (EventBus, DI Container, ConfigManager, Telemetry, Policy, Cancellation) shall never contain business logic. They may validate, route, authorize, observe, or enrich execution metadata, but business decisions must remain inside the Runtime layer.

## Rule 249 — Scheduler Separation of Concerns
The Scheduler owns execution order, but never execution behavior. The Scheduler may decide when, where, after whom, and with which resources a workflow or node executes. It must never decide what a capability does, what response to generate, what emotion to express, or what to speak. Behavior and content generation belong strictly to the execution layer and capability runtimes.

## Rule 250 — Capability Isolation
Capability Runtimes shall perform only isolated business operations. They shall never interact directly with the Scheduler, Planner, Workflow Runtime, EventBus, or other Capability Runtimes. All coordination shall occur exclusively through the Execution Runtime.

## Rule 251 — Capability Purity
A Capability Runtime shall behave as a deterministic worker. It shall receive an immutable ExecutionContext and immutable inputs, produce a CapabilityResult, and terminate. It shall not retain workflow state, publish events directly, invoke other capabilities, or coordinate execution outside the Execution Runtime.

## Rule 252 — Resource Ownership
The Resource Manager is the sole authority responsible for granting, reserving, revoking, and releasing resources. No Scheduler component, Execution Runtime, or Capability Runtime may directly manipulate resource ownership.

## Rule 253 — Deterministic Scheduling
Scheduling decisions shall always be deterministic. The Scheduler shall never invoke an LLM, probabilistic model, or AI reasoning engine to decide execution order, priority, preemption, deadlines, or resource allocation.

## Rule 254 — Scheduler Transparency
Every scheduling decision must be explainable after execution. The Scheduler shall emit sufficient metadata (decision reason, effective priority, resource snapshot identifier, and policy evaluation result) to allow deterministic replay and post-execution auditing.

## Rule 255 — Execution Recovery Ownership
The Execution Supervisor Runtime is the sole authority responsible for execution recovery, retry evaluation, timeout intervention, orphan detection, cancellation propagation, and guaranteed resource cleanup. Neither the Scheduler, Execution Runtime, nor Capability Runtime may independently recover failed executions.

## Rule 256 — Capability Purity
Capability Runtimes must behave as deterministic workers. They shall not retain workflow state between executions, cache mutable execution context, or communicate directly with other capabilities. Every execution must be reproducible solely from its inputs and execution context.

## Rule 257 — Behavior Isolation
Behavior Runtimes shall never influence deterministic execution. They may observe, narrate, animate, express emotion, and communicate with the user, but they shall never modify workflow state, scheduling decisions, capability execution, policy enforcement, or resource allocation.

## Rule 258 — Behavior Determinism
Given identical execution events, identical behavior profiles, identical language, and identical context, the Behavior Layer shall produce identical emotional state transitions, narration intents, dialogue, and expressions. Behavior generation must be deterministic unless an explicitly approved variation mechanism is enabled.

## Rule 259 — Emotion Purity
Emotion Runtime shall derive emotional state exclusively from approved behavior triggers and the active Behavior Profile. It shall not inspect execution internals, access long-term memory, invoke AI models, or infer emotional context from arbitrary text.

## Rule 260 — Semantic Narration
Narration Runtime shall never contain localized text, templates, language rules, grammar, punctuation, or conversational wording. It may emit only semantic CommunicationIntent objects.

## Rule 261 — Companionship Over Logging
Narration exists to enhance companionship, not to narrate every system action. If silence provides a better user experience than speech, silence is the correct behavior.

## Rule 262 — Companion First
Every new feature must answer one question before implementation: "Does this improve CHITTI as a desktop companion?" If the answer is no, the feature should be reconsidered, simplified, or implemented as an optional capability rather than increasing architectural complexity.