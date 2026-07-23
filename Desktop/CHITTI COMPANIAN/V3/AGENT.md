# AGENT

This is the constitution for every AI engineer working on CHITTI. **Read this first.**

## Rule 1
**Every line of code must answer one question: *Which user experience does this improve?***
If you cannot answer that question, you must stop and ask for clarification instead of inventing new abstractions.

## Rule 2
**UX Before Logic.** Every new capability must publish its lifecycle (`Started`, `Progress`, `Completed`, `Failed`) through the Event Bus so the Companion UI, logs, Activity Center, and future memory systems can observe the same execution without direct coupling. Never hide execution. Users should always know what CHITTI is doing.

## Rule 3
**Presence Rule.** The Presence Engine is the single authority for everything the user visually perceives. No runtime, capability, service, or widget may directly manipulate UI state. All visual changes must originate from Event Bus events and flow through the Presence Engine.

## Rule 4
**Renderer Independence.** Business logic must never know how CHITTI is rendered. Desktop Widget, Robot Face, OLED, Web Avatar, and Mobile must all consume the same Presence Engine outputs. This guarantees we never rewrite presence.

## Rule 5
**Unified Time & Waiting.** All delayed work, whether triggered by time or by a monitored condition, must flow through the same scheduling infrastructure. Timers, reminders, recurring schedules, and condition-based notifications are different trigger types of the same system.

## Rule 6
**Time Rule.** Every task that waits for something—whether a clock, a recurring schedule, or a monitored condition—must be represented by a ScheduledEvent. No subsystem may invent its own waiting mechanism.

## Rule 7
**Retrieval Rule.** CHITTI always retrieves before reasoning. If information exists locally, it must search local sources before asking an LLM.

## Rule 8
**Local Knowledge First.** All file discovery must use the local File Index before consulting external reasoning. File Intelligence is responsible for retrieval; LLMs are only used to interpret ambiguous requests or explain retrieved content.

## Rule 9
**Discovery Before Understanding.** CHITTI must first identify the correct resource before attempting to interpret its contents. Discovery selects the target; Document Intelligence explains it. These responsibilities must remain separate.

## Rule 10
**Understanding Rule.** Document Intelligence extracts information; it does not decide how that information is interpreted. Parsing, reasoning, and response generation remain separate responsibilities.

## Rule 11
**Observe Before Remember.** Observation records facts, not interpretations. Memory stores validated observations. Reasoning belongs to the Planner. Memory is created from verified observations and completed interactions. CHITTI must not fabricate memory. All long-term memory entries must originate from trusted system events, user conversations, or validated capability results.

## Rule 12
**Awareness Is Intentional.** CHITTI maintains lightweight awareness of the desktop for companion functionality but performs detailed observation only when required by the user or an active capability. It must never create the impression of continuously surveilling the user.

## Rule 13
**Awareness Is Ephemeral.** The Awareness Runtime records recent, verifiable facts for short-term context. It is not long-term memory. Memory is responsible for deciding what observations are retained beyond their natural lifetime.

## Rule 14
**Architectural Stability.** No new runtime may be introduced unless it represents a fundamentally new domain. New functionality should first attempt to extend existing runtimes (Brain, Voice, Presence, Temporal, Awareness, or Memory) before creating another permanent subsystem.

## Rule 15
**Memory Preserves Provenance.** Every semantic fact stored in Memory must reference the episode or evidence from which it was derived. Raw episodes are immutable history; semantic facts are interpretable knowledge built upon that history.

## Rule 33
**LLMs Never Own Truth.** The language model is a reasoning engine, not a source of truth. All persistent knowledge must originate from architecture-managed runtimes (Memory, Awareness, Capabilities, Planner) and never from the model's internal claims alone.

## Rule 34
**Prompt Assembly Is Centralized.** Only the Inference Runtime may assemble prompts for language models. No other runtime or capability may construct prompts or invoke LLM providers directly.

## Rule 35
**Planner Owns Context.** Only the Planner may decide which Awareness, Memory, Capability, or Conversation context is supplied to the Inference Runtime. The Inference Runtime formats and reasons over context but never retrieves or prioritizes it independently.

## Rule 36
**Proactive Assistance Requires Confidence.** CHITTI may initiate assistance only when the Planner has sufficient confidence based on validated observations and historical context. If confidence is below the configured threshold, CHITTI must ask before acting. Repeated declines should reduce proactive frequency through cooldowns and learned preferences.

## Rule 37
**Assistance Must Be Welcome.** Every proactive action initiated by CHITTI must be explainable, confidence-driven, reversible, and respectful of recent user decisions. The Planner must avoid repeating offers that have recently been declined and should gradually personalize proactive behavior based on demonstrated user preferences.

## Rule 38
**Observations Before Interpretation.** Objective observations (applications, windows, documents, directories) must always be preserved separately from derived semantic interpretations (activities, intents, projects). Derived interpretations may change over time as classifiers improve, but raw observations must remain immutable so historical sessions can be reinterpreted without data loss.

## Rule 39
**Intelligence Emerges from Layers.** CHITTI must derive high-level understanding through successive layers of interpretation. Raw observations produce activities, activities produce intent, and intent informs planning. No component may infer high-level intent directly from raw observations without preserving the intermediate evidence.

## Rule 40
**Privacy in Browsing.** Private/Incognito browsing sessions are never reconstructed or persisted. If a browser window is in Incognito/Private mode (where detectable), CHITTI must avoid reading those visits into memory, avoid offering to restore them, and avoid summarizing them.

## Rule 41
**Context Providers produce deterministic evidence.** Evidence must be correlated and compressed before entering Memory. Semantic interpretation belongs exclusively to higher cognitive layers (Memory, Embeddings, Planner) and never to Context Providers.

## Rule 42
**Provider-Agnostic Composition.** Context Providers must emit provider-specific evidence only. EpisodeBuilder is the sole component responsible for constructing provider-agnostic WORK_SESSION episodes. Context Providers must never write directly to Memory or perform cross-provider aggregation.

## Rule 43
**Shared Evaluation.** Shared evaluation logic must remain provider-independent. Algorithms that rank, score, compress, or summarize evidence (e.g., importance scoring) belong to shared evaluators, not individual Context Providers. Context Providers may emit normalized signals, but they must never embed provider-specific ranking heuristics into the shared pipeline.

## Rule 44
**Provider Independence.** Context Providers must be independently executable and testable. A provider shall depend only on shared evidence models and provider interfaces. It must not require the presence of any other Context Provider to produce valid ProviderEvidence. Cross-provider reasoning belongs exclusively to EpisodeBuilder or higher cognitive layers.

## Rule 45
**Provider Data Minimization.** Context Providers must minimize retained evidence. Providers should collect only the smallest deterministic representation necessary for cognition. Large payloads, binary data, and sensitive content must be summarized, hashed, or redacted before entering the Evidence Pipeline.

## Rule 46
**Realtime Observation.** Context Providers observe user interaction, not operating-system history. Providers must prioritize evidence generated during the active WorkSession. Historical operating-system artifacts (registries, recent-file databases, shell histories, etc.) shall be implemented as separate providers or enrichment sources and must never replace realtime session evidence.

## Rule 47
**Identity Normalization.** Shared identity resolution belongs to dedicated resolver services. Context Providers may observe raw resources, but normalization into reusable identities (e.g., workspaces, projects, repositories, resources) must be delegated to shared resolvers to ensure consistent cognition across all providers.

## Rule 48
**Safe Restoration.** Context Providers must observe user intent without performing actions. Restore capabilities may reconstruct environment state (windows, folders, working directories, browser sessions), but they must never automatically replay user actions, execute commands, or modify external systems without explicit Planner authorization and user confirmation.

## Rule 49
**Deterministic Resolution.** Shared identity resolution must be deterministic, local-first, and reusable. Resolvers may inspect local system state required for normalization (such as filesystem structure), but they must never perform semantic inference, background indexing, or provider-specific reasoning. Multiple Context Providers should resolve identical resources into the same Identity instance whenever possible.

## Rule 50
**Canonical Identity.** Identities are canonical. Every real-world entity (project, workspace, repository, document, command, resource) must resolve to a single canonical Identity. Context Providers may observe different representations of the same entity, but Resolvers must normalize them so higher cognitive layers reason about one shared object rather than duplicate representations.

## Rule 51
**Canonical Synthesis.** Cross-provider synthesis must operate exclusively on canonical identities. EpisodeBuilder and higher aggregation layers may merge evidence only when providers resolve to the same canonical Identity. They must never infer equivalence through labels, window titles, or semantic similarity.

## Rule 52
**Deterministic Workflow Reconstruction.** Workflow reconstruction must remain deterministic. Workflow reconstruction may sequence, classify, and relate observed events using timestamps, canonical identities, and deterministic metadata, but it must never infer user goals, intentions, or semantic meaning. Goal inference belongs exclusively to higher cognitive layers (Planner and Memory).

## Rule 53
**Deterministic Outcome Assessment.** Outcome extraction may classify workflow completion, validation state, and execution results using deterministic workflow patterns and observable evidence. It must never infer user intent, project semantics, or business meaning. Those belong exclusively to higher cognitive layers.

## Rule 54
**Evidence-Driven Intent Modeling.** Intent modeling must remain evidence-driven. Intent extraction may propose one or more deterministic intent candidates derived from workflow outcomes and supporting evidence, but it must never select a primary intent, infer project semantics, or establish user goals. Final intent selection belongs exclusively to the Planner.

## Rule 55
**Planner Authority.** The Planner is the sole component authorized to establish an active goal or user intent. Deterministic components may reconstruct history, assess outcomes, and propose intent candidates, but they must never resolve ambiguity or claim final understanding.

## Rule 56
**Goal Continuity.** Goal continuity must be evidence-driven. A goal may continue, pause, complete, or be abandoned only through observable continuity between current reasoning context and previously established goals. The Planner must never assume abandonment solely because a new goal has appeared.

## Rule 57
**Product Delivery.** Every sprint after Sprint 133 must conclude with at least one complete, user-visible capability that can be demonstrated end-to-end from the CHITTI application. Architectural work alone is no longer sufficient to complete a sprint.

---
> [!IMPORTANT]
> **ARCHITECTURE FREEZE: Perception & Cognition Framework (Rules 41–56)**
> The vertical slice spanning deterministic observation, workflow reconstruction, outcome assessment, intent extraction, goal selection, and goal continuity is officially **FROZEN**. No new layers or abstractions should be added to this framework. Future work must consume this foundation to deliver user-facing companion capabilities rather than redesigning the infrastructure.
---

## Rule 34
**Presence Subscribers.** Components that react to presence (UI, audio, hardware, lighting, haptics, telemetry, etc.) must subscribe to `PresenceStateChanged` events independently. The `PresenceEngine` publishes state transitions but must never orchestrate or directly invoke individual subscribers.

## Rule 35
**Subscriber Isolation.** Subscribers to `PresenceStateChanged` must operate independently. A failure, timeout, or exception in one subscriber must never prevent delivery of the event to other subscribers. Event dispatch must isolate subscriber failures and continue processing remaining listeners.

## Rule 36
**Presence is Declarative.** Presence describes what CHITTI is doing, never how it is expressed. States must represent declarative phases of execution (e.g. `LISTENING`, `THINKING`, `WORKING`). They must never define physical or UI mechanisms (e.g. `PLAY_BLUSH`, `NOD_HEAD`). Translating declarative state into expression is the exclusive responsibility of the Expression Runtime.

## Rule 37
**Expression Runtime Coordination.** The Expression Runtime determines what expression should occur and when. Individual output runtimes (visual, audio, servo, lighting, haptics, etc.) determine *how* that expression is rendered on their respective medium. The Expression Runtime must never manipulate output implementations directly.

## Rule 38
**Declarative Expression Assets.** Expression manifests describe desired outputs using symbolic asset identifiers (animation IDs, motion IDs, sound IDs, etc.). Runtime code must never embed file paths, servo angles, or device-specific parameters.

## Rule 41
**Cooperative Cancellation.** Workflow cancellation must be cooperative. Runtimes signal cancellation through a `CancellationToken`; capabilities are responsible for terminating safely at defined cancellation points. The runtime must never forcibly terminate capability execution except during application shutdown.

## Rule 42
**Capability Purity.** Capabilities execute exactly one invocation and return exactly one `ExecutionResult`. They must not implement retries, workflow sequencing, timeout logic, or compensation behavior.

## 1. What CHITTI Is
CHITTI is a local-first, privacy-respecting, extensible Desktop AI Companion designed for Windows.

## 2. What CHITTI Is Not
CHITTI is not a cloud service, not an abstract research framework, and not an autonomous scraper.

## 3. The Freeze
*   **Folder structure is frozen.** Do not move or restructure directories.
*   **Blueprint is frozen.** Do not attempt to redesign the architecture.
*   **Never redesign architecture.** Work within the established runtimes.
*   **Never exceed MVP.** Do not build features outside of the v1.0 scope.

## 4. The Sprint
*   **One experience per sprint.** The output of a sprint is a working feature, not just infrastructure.
*   Every sprint ends with a **Live Demonstration**.

## 5. Output Format
When communicating task completion, return exactly:
*   Files changed
*   Tests added
*   Validation results
*   Known issues
*   Recommendation for the next sprint

## 6. Coding Standards
Follow Python best practices (PEP8), ensure type hinting, write testable functions, and never duplicate business logic.
