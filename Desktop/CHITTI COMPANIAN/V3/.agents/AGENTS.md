# Engineering Rules

## Rule 18 – The DecisionEngine is pure
No Event Bus, No Logging, No Network, No Files, No Memory Writes, No Skill Calls, No Timers, No Sleep, No Async.
Given the same `PlanningContext`, it must always return the same `Decision`.

## Rule 19 – Workflow primitives are versioned
e.g., `InvokeCapabilityV2`. Existing workflows continue working to avoid migration headaches.

## Rule 20 – Decision confidence is advisory only
The planner shouldn't blindly reject low confidence decisions. Policies decide (e.g. ask user instead of guess). Confidence becomes data, not behavior.

## Rule 21 – Every workflow should be replayable
Workflows must be immutable, deterministic, contain complete parameters, and have no hidden state so they can be replayed months later for debugging.
*(Note: Additionally, CHITTI must always prefer graceful degradation and reduced functionality over termination for optional providers).*

## Rule 22 – Separate Events from State
State (`Planning`, `Idle`, `Waiting`, `Blocked`) is different from Events (`PlannerStarted`, `PlannerFinished`, `PlannerCancelled`). They solve different problems.

## Rule 23 – Everything should produce telemetry
Every subsystem should expose Latency, Queue Depth, Failure Count, Retry Count, Execution Time, and Memory Usage.

## Rule 24 – Runtime Isolation
No runtime may invoke another runtime's public behavior directly. Cross-runtime orchestration must occur through the Runtime Kernel using workflows or well-defined runtime services. This keeps the platform observable, replayable, and deterministic.

## Rule 25 – Runtime Idempotency
Every workflow step must be safe to retry or explicitly declare itself non-idempotent.

## Rule 26 – Executor Never Makes Decisions
The executor executes. Nothing else. It must never contain logic like `if confidence < 0.5: ask_user()` or `if memory_hit: skip_llm()`. Those are planning decisions.

## Rule 27 – Workflow Steps are Atomic
Workflow steps either succeed entirely or fail entirely. There are no partial successes.

## Rule 28 – Kernel Owns Lifecycle
Only the Runtime Kernel may transition a workflow's state (Queued, Running, Retrying, Completed, Cancelled, Failed). Runtimes and Executors only report results.

## Rule 29 – Runtime Results Are Declarative
Runtimes report outcomes; they never determine subsequent actions. Only the Runtime Kernel (or a future planner) decides what happens next based on the returned ExecutionResult.

## Rule 30 – Workflow Versioning
Every persisted workflow must include schema version, planner version, and runtime version to guarantee long-term replayability and migration safety.

## Rule 31 – Capabilities are Stateless
Capabilities must not retain conversational or workflow state between invocations. State belongs in the Memory Runtime, Workflow, or Planner.

## Rule 32 – Capabilities Never Speak Directly
Capabilities should never invoke TTS directly (e.g., `tts.say(...)`). Instead, they return an `ExecutionResult(output="...")`, which the Workflow uses to invoke the Expression Runtime.
## Rule 34 – Memory Is Append-First
Historical interactions should be appended before they are summarized or consolidated. Never skip the episode logging.

## Rule 35 – Facts Are Derived
A capability should never directly write facts (e.g., `favorite_movie = Interstellar`). Instead, they must be validated through the Semantic Memory fact validation pipeline before persistence.

## Rule 36 – Memory Reads Are Cheap, Writes Are Explicit
Reads can happen freely via `MemoryAPI`. Writes should remain explicit workflow actions (e.g., `PersistEpisode`) to preserve observability and replayability.

## Rule 33 – Memory Access Isolation
The Planner and Capabilities may only access memory through `MemoryAPI`. No component outside the Memory Runtime may read or write storage directly.

## Rule 37 – Providers Are Interchangeable
Providers are interchangeable. The Planner must never reference specific providers (e.g., Ollama, LM Studio, OpenAI) in its workflows or execution logic.

## Rule 38 – Prompt Construction Belongs Outside Providers
Prompt construction belongs outside providers. Providers receive normalized `LLMRequest` objects; they never build prompts. That responsibility belongs to the Inference Runtime's Prompt Builder.

## Rule 39 – Streaming Is A UI Concern
Generation can stream via events for UI responsiveness, but workflow completion cannot. The workflow step completes only after the final `ExecutionResult` exists.

## Rule 40 – Inference Providers Are Stateless
Providers must never remember previous prompts, conversation history, or user identity. They receive all required context in the `LLMRequest`. That keeps providers interchangeable.

## Rule 41 – PromptBuilder Owns Prompt Evolution
If you later improve prompting (chain-of-thought suppression, XML formatting, JSON mode, retrieval augmentation), only PromptBuilder changes. Providers stay untouched.

## Rule 42 – InferenceRuntime Never Owns Memory
Conversation state belongs exclusively to Memory Runtime. Inference Runtime should forget everything after producing an `ExecutionResult`.

## Rule 43 – Expression Never Changes Cognition
Expressions are outputs, never inputs. The avatar should never influence planning.

## Rule 44 – One Primary Expression At A Time
Background effects are overlays. Never have conflicting primary states (Thinking, Speaking, Sleeping) simultaneously.

## Rule 45 – Expressions Originate From Workflows
Don't allow arbitrary UI code to trigger expressions. Everything stays observable through the Expression Runtime.

## Rule 46 – Platform First
New functionality must first be evaluated as a Capability before modifying any Runtime or the Runtime Kernel. Only if something fundamentally cannot be implemented as a capability should you consider changing a runtime.

## Rule 47 – Developer Tooling Is Observational
Developer tooling is observational by default. The console should never change runtime behavior unless the developer explicitly enables a debug action. Observation should be side-effect free.

## Rule 48 – Every Event Is Inspectable
Every EventBus event must be inspectable. If it exists, it should be visible somewhere, even if filtered.

## Rule 49 – Replayable Workflows
Every workflow must be replayable from the Developer Console. Replay becomes the killer feature for debugging.

## Rule 50 – Avatar Assets Are Data, Not Code
Profiles define mappings and renderers display assets. Code must never hardcode filenames. Changing avatars or themes should happen purely through data configuration.

## Rule 51 – Capabilities are Product Features
Every user-facing feature should be implemented as one or more capabilities before considering runtime changes.

## Rule 52 – Proactive Privacy
Capabilities must never proactively access sensitive user data without an explicit user request or an active workflow requiring it (e.g. automatic clipboard reading is strictly prohibited).

## Rule 53 – Presence Is Independent
Presence must never influence planning, reasoning, or expressions. It controls only desktop visibility.

## Rule 54 – Background Availability
Docked does not mean inactive. All Runtime subsystems continue operating while CHITTI is docked.

## Rule 55 – Important Events Wake Presence
Only workflows above the configured priority threshold may request CHITTI to become visible.

## Rule 56 – Presence Never Interrupts Interaction
Presence transitions must never interrupt Listening, Thinking, Speaking, or Active workflows.

## Rule 57 – Presence Reversibility
Presence transitions must always be reversible without losing interaction state. Docking and undocking never interrupt or reset interaction state.

## Rule 58 – Capability Permissions
Every capability must explicitly declare its permission scope (e.g., network, filesystem, desktop_control, notifications, clipboard, camera, microphone). Capabilities may never perform actions outside their declared permissions.

## Rule 59 – Browser Runtime Owns Web Interaction
Capabilities must never fetch, scrape, or parse web content directly. All browser navigation, DOM interaction, and webpage extraction must be performed exclusively through the Browser Runtime.

## Rule 60 – Browser Runtime Is Single Owner
Only the Browser Runtime may control browser automation. Capabilities, planners, or inference providers must never directly invoke Playwright, Selenium, or browser APIs.

## Rule 61 – Browser Runtime Preserves User Trust
Browser automation must always remain observable to the user. CHITTI must not perform hidden browser interactions that could surprise the user. Long-running or sensitive browser actions should be visible and interruptible.

## Rule 62 – Task Orchestrator Owns Long-Running Goals
Long-running, multi-step objectives must be orchestrated exclusively by the Task Orchestrator. The Action Planner remains stateless and produces only the initial routing decision.

## Rule 63 – LLMs Never Produce Executable Workflows
Language models may propose task steps or intentions, but only the Workflow Builder may translate them into immutable Workflow primitives.

## Rule 64 – Tasks Own Goals
A Task is the only owner of a long-running user goal. Workflows are transient execution units created to satisfy a Task and must never outlive their parent Task.

## Rule 65 – Observations Are Immutable
Execution observations recorded by the Task Orchestrator are append-only. New reasoning may reinterpret observations, but historical observations must never be modified.


## Rule 66 – Tasks Require Recovery
Tasks must recover from transient failures whenever possible before entering the Failed state.

## Rule 67 – Dangerous Actions Require Approval
Any workflow that modifies user data, installs software, deletes content, executes binaries, or performs similarly impactful actions must obtain explicit user approval before execution.

## Rule 68 – Tasks Are Checkpointed
Long-running tasks must periodically create immutable checkpoints so execution can resume safely after interruption.

## Rule 69 – Task Progress Is Observable
Every running task must expose progress, current activity, elapsed time, and waiting state through the EventBus for inspection by the UI and developer tools.

## Rule 70 – Task Identity is Immutable
Once created, a Task ID and its parent Goal relationship may never change. Recovery, checkpoints, telemetry, approvals, and observations must always reference the original Task identity.

## Rule 71 – Templates Are Declarative
A Task Template describes what should happen, never how it is implemented. Execution logic belongs to the Runtime Kernel and Capabilities.

## Rule 72 – Templates Are Immutable During Execution
Once a Task Template has been instantiated for a task, its compiled structure must remain immutable. Any template modification requires a new template version and new task instantiation.

## Rule 83 – Perception Produces Observations, Never Decisions
Vision, speech, desktop capture, and sensors may only publish observations. Attention may prioritize observations. Only the Planner determines actions. No perception component may trigger capabilities directly.

## Rule 84 – Semantic Runtimes Produce Canonical Objects Only
Entity Extraction, Resolution, Perception, and Memory must publish typed semantic objects. Raw provider outputs (text, pixels, OCR strings, sensor values) must not propagate beyond their respective runtimes. Planning and execution operate exclusively on canonical domain models.

## Rule 85 – Context Is a Read-Only Projection of System State
The Context Engine aggregates information from language, perception, memory, desktop state, and tasks. No runtime may modify another runtime's internal state through the context. Planning consumes context; it does not mutate it. Changes to system state must occur only through the appropriate runtime or capability.

## Rule 86 – Runtimes Publish Facts, Never Beliefs
A runtime may publish only what it directly observes or deterministically derives. Confidence values must accompany uncertain observations. Assumptions, hypotheses, and inferred intentions belong exclusively to the Planner (or a future reasoning layer), not to perception or semantic runtimes.

## Rule 87 – Identity Resolution Enriches Facts, It Never Changes Them
Entity Resolution may attach identifiers, aliases, and metadata to canonical entities. It must not alter the original observed data. If no deterministic match exists, the original entity continues unchanged. Speculative identity inference remains the Planner's responsibility.

## Rule 88 – Identity Is Stable Across Modalities
A single real-world entity must resolve to the same EntityID regardless of whether it was recognized through speech, vision, desktop interaction, memory retrieval, or future sensors. Modality-specific observations may differ, but identity remains invariant. Resolution is the only runtime authorized to bind observations to persistent identities.

## Rule 89 – Temporal Runtimes Record State Changes, Never Interpret Them
Observation History records appearance, disappearance, duration, and transitions. It must not infer motives or events (e.g., "user left", "meeting started"). Interpretation belongs to the Planner or a future World Model Runtime.

## Rule 90 – World State Is Derived, Never Stored
Observation History records temporal facts. The World Model derives the current state from those facts. The Planner consumes the derived state. No runtime manually edits the world state.

## Rule 91 — World Models Describe the Present, Activity Models Describe the Past
The World Model represents the current derived state of the environment. Activity and Timeline runtimes record historical sequences of work. Neither runtime owns the other's responsibility. The Planner may consume both simultaneously.

## Rule 92 — Activity Runtimes Record Work, Never Infer Purpose
The Desktop Activity Runtime records factual work sessions (applications, windows, timings, transitions). It must not infer what the user was trying to accomplish. Associating activities with projects, goals, or productivity metrics belongs to higher-level runtimes such as the Goal & Project Runtime or Productivity Analytics Runtime.

## Rule 93 — Activity Runtime Records Facts Only
The Activity Runtime never summarizes activity or attributes high-level meaning (e.g., "User worked on AI project"). It strictly records objective, chronological facts. Inferences and summaries belong strictly to higher-level analytical runtimes and inference pipelines.

## Rule 94 — Activity Records Are Immutable
Once an activity record is persisted to the database, it must never be altered or updated. Corrections or additions must be made as new events, not destructive edits to historical facts. This ensures auditability and deterministic replay.

## Rule 95 — Goal Runtime Tracks Intent, It Does Not Infer Intent
The Goal Runtime maps deterministic activity records to higher-level intentions (Goals and Projects) through known associations. It must never use LLMs or heuristics to guess or infer what the user is working on. Ambiguity or unknown workspaces result in UNMAPPED_ACTIVITY events that the Planner (or a reasoning layer) is responsible for resolving.

## Rule 176 — The Memory Hierarchy
Observations are transient. Episodes are durable. Knowledge is permanent.

## Rule 240 — Channel Routing Enforcement
The Android Companion (or any external client) must never directly invoke capabilities or manipulate the execution pipeline. Every request from Android must enter the Conversation Runtime through the Channel Router exactly as if it originated from voice or local desktop UI.

## Rule 241 — Communication Session Origin
Every user interaction shall originate from exactly one Communication Session. No runtime may infer or create user interactions outside an active session except notifications explicitly initiated by CHITTI.

## Rule 236 — Referential Transparency
A valid Workflow deterministically invokes a capability and emits the correct immutable ExecutionEvents. Given the same workflow state, execution must produce the identical sequence of events.

## Rule 237 — No Runtimes Without Jobs
Every new abstraction or implementation detail in Layer 1 (Cognitive Capability Bring-up) must be motivated by a new Cognitive Benchmark Job. Define the job first, then implement the capability required to pass it.

## Rule 238 — Every Benchmark Must Exercise the Entire Spine
No cognitive benchmark may test a runtime component in isolation (e.g. Planner.generate() directly). Every benchmark must start from a User Goal and run entirely through Context, Planning, Translation, Execution, and Evaluation to guarantee architectural integrity.

## Rule 239 — Companion Framework Freeze Rule
A new model may only be added to the Companion Framework if it represents a semantic concept shared by three or more independent features. Otherwise, the model belongs inside the feature that introduced it.

## Rule 134 — Memory Hierarchy
Observations are transient. Episodes are durable. Knowledge is permanent.

## Rule 135 — Progressive Consolidation
Memory is consolidated progressively rather than periodically deleted.

## Rule 136 — Memory Traceability
Higher-level memories are derived from lower-level memories and retain traceability to their source episodes.

## Rule 137 — Optimizing for Continuity
Recommendations must optimize user continuity rather than abstract productivity metrics.

## Rule 138 — Cost of Interruption
CHITTI must never interrupt focused work unless the expected value of the interruption exceeds the estimated disruption cost.

## Rule 139 — Explainable Recommendations
Every proactive recommendation must be explainable. Users must know why a suggestion was made.

## Rule 140 — Assistant Platform Composition
Assistants compose platform capabilities. They never duplicate platform functionality.

## Rule 141 — Assistant Experience Ownership
Assistants own user experience, not infrastructure.

## Rule 142 — Assistant Autonomy and Explainability
Every autonomous assistant action must be explainable, reversible when practical, and traceable through the Cognitive Trace.

## Rule 143 — Assistant Continuity Optimization
Assistants optimize for continuity of user goals rather than completion of isolated commands.

## Rule 144 — Assistant Communication via Planner
Assistants communicate through goals and capabilities, never by invoking other assistants directly.

## Rule 145 — Assistant UX Ownership
Assistants own conversation and user experience. Planning and execution remain platform responsibilities.

## Rule 999 — Sprint E.2 Freeze Rule
No new features may be added until every command in the Dogfood Matrix passes end-to-end through the real production pipeline.

## Rule 146 — Coding Assistant Prerequisites
Before proposing code changes, the Coding Assistant must establish project, context, memory, and continuity.

## Rule 147 — Assistants Never Inspect the Environment Directly
Assistants must obtain environment information exclusively through observation/world runtimes. Products never talk directly to desktop integrations.

## Rule 148 — Knowledge Traceability
Every synthesized knowledge claim must remain traceable to its originating evidence throughout its entire lifecycle.

## Rule 149 — Passive Preparation
Preparation is reversible. Persistence requires user approval.

## Rule 150 — Knowledge Explainability
Every generated knowledge modification must remain explainable through explicit supporting evidence. The assistant must never silently rewrite knowledge without providing a reviewable reason.

## Rule 151 — Product Cognitive Pipeline
Every Product Assistant must follow a uniform execution model: Observation -> Context Recovery -> Domain Analysis -> Goal Detection -> Passive Preparation -> Suggestion -> Planner Execution.

## Rule 152 — Risk Overrides Autonomy
No assistant may execute an action whose risk level exceeds the platform's current approval policy, regardless of the assistant's autonomy setting.

## Rule 153 — Assistants Describe Intent, Never Mechanism
Assistants must output high-level intent (e.g., 'Open invoice', 'Extract total') and never low-level UI mechanisms (e.g., 'Click X', 'Wait 500 ms'). Mechanism belongs exclusively to the Execution Runtime.

## Rule 154 — Assistants Preserve Cognitive Continuity
Whenever a user transitions between major contexts, assistants must preserve and restore working context through platform runtimes rather than local state.

## Rule 155 — Knowledge Is Never Invented
Every synthesized answer must distinguish between retrieved knowledge, inferred conclusions, and unresolved gaps. This keeps hallucination risk extremely low.

## Rule 156 — Adaptive Preferences Require Proportional Consent
The permanence and impact of a profile change determine the level of user approval required. Small reversible changes may happen automatically; long-term behavioral changes require confirmation; identity changes require explicit declaration.

## Rule 157 — User Profiles Are Explainable
Every adaptive preference must identify the evidence that produced it and whether it was inferred automatically or explicitly confirmed.

## Rule 158 — Synchronization Replicates State, Handoff Transfers Ownership
Synchronization and handoff are fundamentally different architectural concepts. Synchronization copies knowledge eventually; handoff transfers execution immediately. They must never share implementation.

## Rule 159 — Single Owner of Execution
At any moment, exactly one device owns execution of a workflow. Knowledge may exist everywhere, but execution has exactly one owner to prevent distributed conflicts.

## Rule 160 — Plugins Never Depend on Other Plugins
Plugins communicate exclusively through platform-defined interfaces and shared runtimes. Never allow direct Plugin-to-Plugin communication.

## Rule 161 — Plugins Extend Capabilities, Not Cognition
Plugins may contribute capabilities but may not modify planner behavior, platform rules, or core runtime logic. The Planner remains exclusively trusted.

## Rule 162 — Declarative Interfacing
Plugins interact with the platform exclusively through declarative APIs, CapabilityContracts, and PlatformEvents, never through raw runtime internals.

## Rule 163 — Inference Requests Describe Capabilities, Never Specific Models
Inference requests must specify required capabilities (e.g., reasoning level, latency, modality), never specific model names. Assistants remain model-independent forever.

## Rule 164 — Model Selection is a Scheduling Decision
Model selection is a scheduling concern owned exclusively by the Compute/Model Manager Runtime. Assistants and Planners do not select models.

## Rule 165 — Updates Are Transactional
Platform updates are transactional. Partial updates must never leave CHITTI in an inconsistent state. They must either fully commit or fully rollback via a Recovery Point.

## Rule 166 — Continuity Ownership
Runtime continuity is restored exclusively through the Continuity Runtime. The Update Runtime only acts as the orchestrator and must never reconstruct cognitive continuity itself.

## Rule 167 — Backups Preserve Logical State
Backups preserve logical platform state, not transient execution state. The Backup Runtime must not attempt to archive things that belong to the Continuity Runtime (e.g., active task memory).

## Rule 168 — Verifiable Backups
Every backup must be independently verifiable before it is considered complete. An unverified backup should never appear as "successful."

## Rule 169 — All External Interfaces Express User Intent
All external interfaces express user intent. Internal runtimes determine execution. Desktop UI, mobile apps, voice, REST APIs, and plugins all submit intent in exactly the same way. The Planner remains the sole authority on how to interpret and execute that intent.

## Rule 170 — Interaction and Execution Ownership Are Independent
Interaction and execution ownership are independent. A remote device can own the interaction while the desktop owns execution. Only an explicit handoff changes execution ownership.

## Rule 171 — Every External Request Is Policy Evaluated
Regardless of origin (desktop, mobile, web, plugin, or API), every request must pass through the platform's authorization, risk, and policy evaluation before reaching the Planner.

## Rule 172 — The Runtime Kernel Orchestrates, Runtimes Decide
The Runtime Kernel is responsible only for lifecycle management, dependency composition, and event routing. All domain logic, planning, execution, and decision-making must reside within runtimes. The Kernel must remain policy-neutral and deterministic.

## Rule 173 — Runtime Dependencies Must Be Explicit
Every runtime shall explicitly declare its required service dependencies. The Runtime Kernel is solely responsible for dependency resolution and initialization order. Runtimes must never discover or instantiate other runtimes dynamically.

## Rule 174 — Interaction Transports Translate, They Do Not Decide
Interaction Transports are responsible only for converting external inputs and outputs into standardized interaction and expression models. They must never contain planning, workflow, policy, or execution logic.

## Rule 175 — Memory Stores Facts, Never Decisions
The Memory Runtime records interactions, context, and state exactly as they occur. It must never infer intent, summarize conversations, rank importance, or perform reasoning. Interpretation belongs exclusively to the Planner and higher cognitive runtimes.

## Rule 176 — The Planner Formulates Plans, Never Executes Them
The Planner Runtime transforms interactions and memory into immutable execution plans. It must never invoke capabilities, modify hardware, generate user-visible output, or perform execution directly.

## Rule 177 — Execution Enforces Plans, Never Modifies Them
Execution may track runtime state through `WorkflowContext`, but it must never alter an `ExecutionPlan`.

## Rule 178 — Capabilities Are the Only Units of Execution
Every executable action must be implemented as a registered capability. The Execution Runtime must never contain workflow-specific execution logic or action-specific branches.

## Rule 179 — Expression Never Influences Cognition
The Expression Runtime may transform presentation, formatting, or media, but it must never alter plans, memory, execution state, or cognitive decisions.

## Rule 180 — Every User-Visible Response Originates From Execution
All user-visible expressions must originate from a successfully executing capability. Transports, renderers, and user interfaces must never generate responses independently.

## Rule 181 — Rendering Is Lossless
The Expression Runtime may enrich presentation (formatting, SSML, HTML, metadata), but it must never change the semantic meaning of an expression. Meaning belongs to cognition, presentation belongs to expression.

## Rule 182 — Deterministic Infrastructure, Non-Deterministic Intelligence
The Runtime Kernel, Memory Runtime, Planner Runtime, Execution Runtime, Expression Runtime, Capability system, and Transport layer shall remain deterministic. Non-deterministic reasoning is permitted only within explicitly designated inference strategies. All outputs of inference must be transformed into deterministic execution plans before entering the cognitive pipeline.

## Rule 183 — Inference Produces Decisions, Never Side Effects
Inference strategies may interpret, reason, rank, or generate planning decisions. They must never access hardware, modify memory directly, invoke capabilities, emit expressions, or execute workflows. All externally observable behavior must flow through the deterministic cognitive pipeline.

## Rule 184 — Inference Is Advisory
Inference strategies may classify, extract, rank, or recommend, but they do not create execution plans directly. The Planner Runtime remains the sole authority responsible for converting inference into deterministic planning decisions.

## Rule 186 — Provider Diversity Shall Not Affect Planning
Differences between inference providers shall be normalized within the Provider Layer and Inference Validator. The Planner Runtime shall receive provider-independent inference results and must never contain provider-specific logic.

## Rule 187 — Provider Selection Is Infrastructure
Selecting, routing, retrying, or failing over between inference providers is an infrastructure concern. Planning strategies shall request inference through the Inference Manager and must remain unaware of provider identity, routing decisions, or availability.

## Rule 188 — Prompt Construction Is Deterministic
PromptBuilder shall construct prompts exclusively from deterministic inputs (configuration, templates, memory snapshots, interaction context, and provider capabilities). Prompt construction must not invoke inference, perform reasoning, or introduce nondeterministic behavior.

## Rule 189 — Every Inference Must Be Reproducible
Every inference request shall carry sufficient metadata (prompt version, content hash, provider, model, configuration, and correlation ID) to reproduce or replay the request for debugging, benchmarking, or regression analysis. Reproducibility is an infrastructure concern and must not depend on external provider state.

## Rule 190 — Operational Data Is Not User Memory
Replay logs, telemetry, diagnostics, benchmarks, and performance records exist exclusively for system observation and debugging. They must remain physically and logically separate from user memory, conversation history, and cognitive state.

## Rule 191 — Routing Decisions Must Be Explainable
Every planning-route decision shall be derived exclusively from deterministic policy inputs and must emit sufficient metadata to explain why a particular strategy was selected. Routing decisions shall never depend on hidden or non-reproducible state.

## Rule 192 — Context Selection Determines Relevance, Not Truth
Context selectors rank and prioritize existing memory for inference. They must never summarize, rewrite, infer new facts, or modify stored memory. Their responsibility is limited to selecting which evidence enters the prompt.

## Rule 193 — Context Selection Must Be Explainable
Every selected memory item shall have a deterministic justification for its inclusion. Context selection algorithms must emit sufficient metadata to explain why an item was selected or discarded. This explanation is operational telemetry and must remain separate from user memory.

## Rule 194 — Clarification Preserves Intent
Clarification workflows shall refine incomplete planning decisions without replacing or reinterpreting the original intent. Until explicitly abandoned, the original intent remains authoritative and subsequent clarification responses are interpreted relative to that pending intent.

## Rule 195 — Clarification Resolves One Ambiguity at a Time
A clarification workflow shall request only the single highest-value missing parameter required to continue deterministic planning. Multiple ambiguities shall be resolved through successive clarification turns rather than compound questions.

## Rule 196 — Capability Recommendations Are Advisory
Capability recommendations generated by inference are advisory only. The Planner must deterministically validate every recommended capability against the registry, permission policies, and parameter schema before constructing an ExecutionPlan. Unvalidated recommendations shall never be executed.

## Rule 197 — Embeddings Are Immutable
Embeddings associated with a memory record are immutable. Any semantic change to the memory requires generating a new embedding rather than modifying the existing vector in place.

## Rule 198 — Retrieval Never Generates Data
Semantic Retrieval may rank, filter, and retrieve existing memories only. It must never synthesize, infer, summarize, or alter memory contents.

## Rule 199 — Semantic Retrieval Selects Evidence, Never Conclusions
Semantic retrieval may retrieve, rank, and filter memory based on similarity, but it must never infer, summarize, synthesize, or conclude. All interpretation remains the responsibility of the Inference Layer.

## Rule 200 — Knowledge Is Hierarchical
Knowledge ingestion shall preserve information at multiple abstraction levels (summaries, concepts, and atomic facts). Retrieval policies determine the appropriate level for inference. No single representation is universally optimal.

## Rule 201 — Extracted Knowledge Requires Provenance
Every persisted knowledge record shall retain immutable references to its originating document, chunk, extraction process, and embedding metadata. Knowledge without provenance shall not be persisted.

## Rule 202 — Knowledge Sources Are Format-Agnostic
Knowledge ingestion operates on normalized `KnowledgeSource`s rather than document types. Extraction, validation, and persistence must remain independent of the original storage or transport format.

## Rule 203 — Relationships Are First-Class Knowledge
Relationships shall be stored, validated, versioned, and traced independently of the knowledge records they connect. A relationship is itself a knowledge artifact with its own provenance and confidence.

## Rule 204 — Graph Expansion Is Policy Driven
Retrieval may expand through knowledge relationships only according to an explicit `RetrievalExpansionPolicy`. Expansion policies define traversal depth, relationship types, confidence thresholds, and expansion budgets. Retrieval implementations shall never perform unrestricted graph traversal.

## Rule 205 — Knowledge Graph Integrity
The Knowledge Validator is solely responsible for enforcing graph integrity, including dangling references, invalid self-links, prohibited relationship types, and graph consistency rules. Extraction strategies may propose graphs but shall never guarantee structural correctness.

## Rule 206 — Knowledge Identity Is Stable
The identity of a knowledge record shall be established through deterministic identity resolution using provenance and structural evidence rather than textual similarity alone. Changes in wording must preserve identity whenever the underlying knowledge remains unchanged.

## Rule 207 — Identity Is Independent of Evidence
A Knowledge Identity represents a canonical concept. Knowledge Records represent supporting evidence from individual sources. Multiple records may support one identity while preserving independent provenance, version history, and confidence.

## Rule 208 — Evidence Never Modifies Identity Directly
Knowledge Records contribute evidence toward an identity but shall never directly alter the structure or relationships of a Knowledge Identity. Identity evolution must occur exclusively through deterministic identity resolution.

## Rule 209 — Retrieval Must Preserve Evidence
Retrieval shall never collapse multiple supporting records into a single synthesized fact. The originating evidence supporting every retrieved identity must remain available throughout planning and expression.

## Rule 210 — Conflict Detection Is Advisory
Intelligence may propose conflicting evidence, but only deterministic validation may create or resolve `KnowledgeConflict` records.

## Rule 211 — Conflicts Are Evidence, Not Identity
Conflicts exist between supporting evidence and shall never directly alter the lifecycle of a `KnowledgeIdentity`. Identities remain stable while conflict records describe disagreements among their supporting evidence.

## Rule 212 — Knowledge Availability Precedes Knowledge Analysis
Validated knowledge shall become immediately available for retrieval after persistence. Analytical processes such as conflict detection, consensus scoring, trust evaluation, and graph optimization shall execute asynchronously and must never delay knowledge availability.

## Rule 213 — Analytical Results Are Derived State
Conflicts, consensus scores, trust metrics, and similar analytical artifacts are derived from persisted knowledge. They may be regenerated at any time and shall never be treated as the authoritative source of truth.

## Rule 214 — Analysis Modules Are Independent
Knowledge analysis modules (Conflict, Consensus, Trust, Optimization, etc.) shall operate independently through the Analysis Scheduler. No analysis module may directly invoke another. Dependencies between analyses shall be resolved through scheduling policies rather than direct coupling.

## Rule 215 — Analysis Targets Immutable Versions
Every analysis result shall reference the specific version of the knowledge graph on which it was computed. When the underlying knowledge changes, previous analysis results become stale rather than silently updating.

## Rule 216 — Analysis Never Mutates Knowledge
Knowledge analysis modules may generate, update, or invalidate analytical artifacts, but they shall never modify `KnowledgeIdentity`, `KnowledgeRecord`, `KnowledgeRelationship`, or `KnowledgeProvenance`. Any change to knowledge must occur exclusively through the Knowledge Pipeline.

## Rule 217 — Authority Is Policy, Trust Is Analysis
Authority is an immutable property assigned to a knowledge source according to deterministic policy. Trust is a derived analytical assessment that may evolve as new evidence is evaluated. Authority shall never be modified by analytical processes.

## Rule 218 — Evidence Evaluation Must Be Explainable
Every evidence ranking or weighting decision shall expose the individual deterministic factors contributing to the final evaluation. Composite scores shall never obscure their underlying reasoning.

## Rule 219 — Evidence Evaluation Is Contextual
Evidence evaluation is computed for a specific reasoning context and shall not be permanently persisted. Only the analytical artifacts from which it is derived (Authority, Trust, Consensus, etc.) may be stored.

## Rule 220 — Graph Maintenance Preserves Knowledge
Graph maintenance may optimize indexes, caches, and analytical artifacts but shall never remove authoritative knowledge. Removal or deprecation of knowledge shall occur only through the Knowledge Pipeline.

## Rule 221 — Goals Never Own Context
Goals represent desired outcomes only. Context required to achieve a goal shall be assembled dynamically during planning and must never be permanently embedded within the goal itself.

## Rule 222 — Goals Are Declarative
A Goal defines only the desired outcome. It shall never prescribe implementation details, execution order, required knowledge, or workflow mechanics.

## Rule 223 — Plans Are Declarative Contracts
A Plan describes the intended sequence of steps, decisions, and constraints required to achieve a Goal. It must contain no execution logic, state management, or runtime algorithms.

## Rule 224 — Plans Are Immutable During Execution
Once a Plan transitions out of the DRAFT state, it becomes an immutable contract. Any changes in strategy required by execution failures must result in the generation of a new Plan (replanning), which supersedes the previous one.

## Rule 225 — Plans Describe Intent, Not Capability Selection
A Plan shall express semantic actions only. Mapping those actions to platform capabilities is the exclusive responsibility of the Workflow Translator.

## Rule 226 — Workflows Are Executable Contracts
A Workflow maps a Plan's semantic intent directly into specific platform capabilities, execution policies, and data payloads. It is a strictly deterministic execution graph containing no planning heuristics.

## Rule 227 — Workflows Never Plan
A Workflow must execute its steps exactly as defined. If an unexpected failure occurs that cannot be resolved via its declared `ExecutionPolicy`, the Workflow must transition to FAILED and yield control back to the Planner. The Workflow Runtime must never dynamically invent new steps to recover.

## Rule 228 — Workflows Bind Intent to Capability
A Workflow is the sole architectural layer permitted to bind semantic planning intent to concrete platform capabilities. Neither Plans nor the Execution Runtime shall perform capability selection.

## Rule 229 — Context Assembly Is Deterministic
The `GoalContextBuilder` shall only use deterministic retrieval policies, graph traversal, and established evaluation metrics (Trust, Authority, Consensus) to assemble context. It must never use language models, inferences, or probabilistic heuristics to guess what context might be useful.

## Rule 230 — Planners Must Not Fetch Context
The `Planner` operates strictly on the `GoalContext` provided to it. The Planner must never perform its own database queries, web searches, or semantic retrievals during the planning phase. If more context is needed to formulate a plan, the Planner must output an explicit `Plan` to acquire it.

## Rule 231 — Context Is Snapshot-Based
A `GoalContext` represents a deterministic snapshot of all relevant knowledge, goals, constraints, and system state at a specific point in time. Once assembled, it shall never change.

## Rule 232 — Planners Only Produce Plans
The `PlannerRuntime` must never perform direct actions, trigger side-effects, or invoke capabilities. Its ONLY acceptable output is a structured `Plan` object or a deterministic failure.

## Rule 233 — Planning Is a Deterministic Pipeline
The transformation of a `GoalContext` into a `Plan` must follow a strict, deterministic pipeline: Context Validation -> Constraint Analysis -> Step Generation -> Dependency Resolution -> Plan Validation. No step generator (including non-deterministic LLMs) is permitted to bypass the validation and resolution layers.

## Rule 234 — Runtimes Are Transformation Contracts
Every cognitive transformation runtime must explicitly implement a formal `TransformationContract`. This contract mandates strict definitions for Input, Output, and Validation Rules. No transformation runtime may operate ad-hoc.

## Rule 235 — Transformations Guarantee Observability
A Transformation Runtime must never execute without producing standardized telemetry via a `TransformationExecutor`. Execution latency, failure reasons, and validation drops must always be recorded into a `TransformationResult`.

## Rule 236 — Transformations Are Referentially Transparent
Given the same immutable input and the same system policy configuration, a Transformation Runtime shall always produce the same immutable output or the same deterministic failure.

## Rule 237 — Translator Must Not Execute or Retrieve
The `WorkflowTranslator` is strictly a binding engine. It maps semantic intents to capability schemas. It must never invoke a capability during translation to "test" it, nor should it perform semantic retrieval to guess bindings. Its transformation must be entirely predictable based on the provided `CapabilityRegistry` and `TranslationPolicy`.

## Rule 238 — Workflows Must Be Fully Bound
A Workflow shall never contain unresolved capability references, parameter bindings, or transition targets. Every Workflow emitted by the Workflow Translator must be immediately executable by the Execution Runtime.

## Rule 239 — Execution Events Are Factual, Not Evaluative
`ExecutionEvents` shall record strictly what happened (e.g., "Capability returned X", "Task timed out"). They must never contain judgements regarding whether the output satisfied the overarching `Plan` or `Goal`. Analysis and evaluation belong exclusively to evaluators.

## Rule 240 — Execution Events Are Append-Only and Immutable
Every `ExecutionEvent` must be persisted immediately upon generation by the `ExecutionRuntime`. Once emitted, it is permanent. If a task is retried, a new event is appended. Historical execution records shall never be overwritten or modified. Workflow summaries must be derived analytically, never replacing the raw event history.

## Rule 241 — Evaluators Consume Events
Workflow Evaluators and Goal Evaluators shall derive their conclusions exclusively from immutable `ExecutionEvent` histories. They shall never infer execution outcomes from mutable runtime state.

## Rule 242 — Workflow Evaluators Assess Execution, Not Intent
The `WorkflowEvaluator` is strictly responsible for determining whether a Workflow executed successfully according to its blueprint. It shall NEVER evaluate whether the overarching `Goal` was satisfied, nor shall it extract knowledge. Its output represents execution success, not goal satisfaction or learning.

## Rule 243 — Assessments Are Derived and Reproducible
A `WorkflowAssessment` is a derived artifact that can always be regenerated deterministically from immutable `ExecutionEvents`. It shall never become the authoritative record of execution.

## Rule 244 — Goal Evaluator Owns Intent Satisfaction
The `GoalEvaluator` is the ONLY runtime authorized to declare whether a user's intent was met. No other component (including the Planner, ExecutionRuntime, or WorkflowEvaluator) may assert goal satisfaction. Its generated `GoalAssessment` represents the canonical truth regarding goal achievement.

## Rule 245 — Goal Assessments Are Immutable
A `GoalAssessment` is a permanent, immutable record of an evaluation at a specific point in time. If a goal is subsequently replanned and re-executed, the new execution will yield a *new* `GoalAssessment`. Historical assessments must never be modified.

## Rule 246 — Goal Satisfaction Is Criterion-Based
A Goal shall be evaluated exclusively against its declared `GoalCriterion` set. Free-form interpretation of goal descriptions shall only be permitted where explicitly marked as requiring semantic evaluation via bounded LLM evaluators. The final satisfaction score must be a deterministic aggregation of these criteria.

## Rule 247 — Consolidation Is Declarative
The `MemoryConsolidator` shall not directly write to the persistent database. It is a pure `TransformationRuntime` that produces a `ConsolidationReport` containing explicitly formatted `KnowledgeRecords` and `HeuristicRecords`. The actual persistence of these records must be handled by the Memory Runtime's internal ingestion process.

## Rule 248 — Learning Preserves Provenance
Every `KnowledgeRecord` or `HeuristicRecord` generated through consolidation shall retain explicit references to the originating `ExecutionEvent` sequence and `GoalAssessment` that justified its creation. This keeps learning fully explainable.

## Rule 249 — Replanning Is Bounded
The `ReplanningRuntime` must deterministically track the lineage of replanning attempts. If a `Goal` repeatedly fails and exceeds its configured `max_replanning_depth`, the Replanner MUST mark the directive as `max_retries_exceeded` and the orchestration layer must transition the Goal to `ABANDONED`. The system must never enter an infinite replanning loop.

## Rule 250 — Planners Consume Directives
When a Planner receives a `PlanningContext` that contains a `ReplanningDirective`, it is legally bound to obey those policy constraints. Directives (e.g., `avoid_capability_ids`) supersede any default planner behavior.

## Rule 251 — Replanning Never Alters History
The `ReplanningRuntime` shall formulate a new planning attempt exclusively through new directives and context. It shall never modify previous `Plan`, `Workflow`, `ExecutionEvent`, or `GoalAssessment` artifacts.

## Rule 96 — Memory Runtime Stores Knowledge, It Does Not Create Knowledge
The Memory Runtime is strictly a persistence and retrieval layer for validated semantic knowledge and episodic records. It must never use probabilistic reasoning, heuristics, or language models to infer new facts, resolve contradictions automatically, or deduce undocumented relationships. All inferences must be performed by the Planner and explicitly persisted via capabilities (e.g. PersistFact).

## Rule 97 — Voice First, Visual On Demand
Never open a presentation automatically unless explicitly requested by the user, or if visual interaction is strictly required to proceed.

## Rule 98 — Runtimes Never Generate HTML
Runtimes return structured data only (e.g., `PresentationModel`). All formatting, structuring, and markup generation is strictly the responsibility of the Presentation Runtime.

## Rule 99 — Presentation Runtime Owns All Rendering
The presentation runtime exclusively handles rendering. No other runtime may implement local HTTP servers, WebSocket bridges, or interact with browser UI generation.

## Rule 100 — HTML Never Contains Business Logic
All computation belongs to capability runtimes. Templates may only loop, format, and display data. 

## Rule 101 — Voice and Presentation Must Be Independent
Modalities are strictly decoupled. The planner decides the response modalities (Speak, Presentation, Both, Neither), not the capability.

## Rule 102 — Browser Must Never Be Trusted
Browser events are requests, never commands. Incoming UI actions must never execute directly. They must be published as PresentationEvents, validated, and routed through the Planner to the Capability Runtime.

## Rule 103 — Presentations Are Ephemeral Unless Explicitly Pinned
Presentation windows exist only to assist the current interaction. Once their purpose is fulfilled, the Presentation Runtime should automatically close them unless the user has explicitly pinned or requested to keep them open.

## Rule 104 — All Visual Output Must Flow Through the Presentation Runtime
No runtime, capability, planner, or workflow may generate UI directly. Everything visual becomes a PresentationModel routed through PresentationService to the Presentation Runtime. No exceptions.

## Rule 105 — The World Runtime Is The Sole Source Of Current Digital State
No runtime, capability, or planner may directly query operating system state. All current-state information must originate from the World Runtime.

## Rule 106 — Analytics Records Facts, Not Interpretations.
Analytics stores completed behavioral facts and derived aggregate metrics. It must never duplicate World state or predict future behavior.

## Rule 107 — Prediction Forecasts Futures; It Never Executes Them.
The Prediction Runtime may only emit forecasts and insights. All proactive behavior must be authorized by the Planner or Automation Runtime.

## Rule 108 — Architectural Freezing of the Cognitive Core
No new core runtime should be introduced unless it represents a fundamentally new cognitive responsibility that cannot be expressed by composing the existing runtimes (World, Activity, Productivity, Analytics, Prediction, Presentation, Memory, Search).

## Rule 109 — Structured Perception Takes Precedence Over Visual Perception
When multiple perception sources describe the same information, CHITTI must prefer structured providers (e.g., Browser Intelligence, IDE providers, Calendar providers) over OCR-derived visual interpretations. Visual Intelligence serves as a semantic fallback for interfaces that lack structured access.

## Rule 110 — Capabilities Describe Intent; Execution Providers Perform Actions
Capabilities must never directly manipulate operating system resources. All physical execution flows through Execution Providers coordinated by the Execution Runtime.

## Rule 111 — Execution Providers are Atomic
Providers perform only primitive OS interactions and must never contain business logic or planning decisions.

## Rule 112 — Execution Plans are Declarative
Execution Plans describe the desired outcome, never the implementation strategy.

## Rule 113 — The Runtime Pattern
No new runtime may be introduced unless it follows the Runtime Pattern established by the World Runtime and Execution Runtime. Every runtime must consistently provide Models, a State Machine, a Registry, Providers, Evidence, Verification, Telemetry, Health, Configuration, and a clear API boundary.

## Rule 114 — Execution Rollbacks are Best-Effort
Providers must restore the previous state whenever technically feasible, but rollback is never guaranteed to perfectly undo external side effects. Expectations should be realistic and avoid assuming rollback is equivalent to database transactions.

## Rule 116 — Model Runtime Is Infrastructure
Model Runtime manages model assets and hardware allocation only. It never performs inference, prompt construction, tokenization, or AI reasoning.

## Rule 117 — Capability-Based Model Selection
AI services request capabilities, not specific models. Model selection is the exclusive responsibility of the Model Runtime.

## Rule 118 — AI Runtime Semantic Interface
AI Runtime exposes semantic capabilities (e.g., generate_text, recognize_speech), never model-specific interfaces.

## Rule 119 — Inference vs Lifecycle Responsibility
AI Runtime owns inference. Model Runtime owns model lifecycle. Never blur those responsibilities.

## Rule 120 — Validated Semantic Output
AI Runtime returns validated semantic objects, never raw model output. No runtime above AI Runtime should parse JSON.

## Rule 121 — Resource Runtime Exclusivity
Resource Runtime observes hardware state. It never allocates or releases resources.

## Rule 122 — Semantic Resource Events
Higher runtimes consume semantic resource events rather than raw hardware metrics.

## Rule 123 — Inference Adaptation
Inference quality adaptation belongs exclusively to the AI Runtime.

## Rule 124 — Architecture Freeze
No new foundational runtime may be introduced unless an architectural deficiency is demonstrated that cannot be solved by extending an existing runtime.

## Rule 125 — Workflow Coordination
Workflow Runtime coordinates execution. It never performs business logic or operating system actions.

## Rule 126 — Workflow Immutability
Workflows are immutable after planning. Only WorkflowState and WorkflowContext may change during execution.

## Rule 127 — Capability Intent Expansion
Capabilities expand workflow intent into execution plans. Workflows never contain operating system primitives.

## Rule 128 — Deterministic Observation Preference
Observation capabilities must always prefer deterministic operating system data over probabilistic AI inference.

## Rule 129 — Vision AI as Augmentation
Vision AI augments observations; it never replaces deterministic system information when such information is available.

## Rule 130 — Semantic Capability Outputs
Capabilities return semantic models, never raw provider outputs.

## Rule 131 — World Runtime Consumption
Capabilities consume world state through the World Runtime rather than invoking other capabilities directly.

## Rule 132 — Context Synthesis Purity
Context capabilities synthesize observations but never collect raw observations themselves.

## Rule 133 — Context Caching
Derived context is cacheable and invalidated by meaningful world changes.

## Rule 250 — Live Demonstration
**Every sprint must end with a live demonstration.** The primary output of a sprint is a working user experience, not just merged code.

## CHITTI AI Integration Constitution

### Rule 1 — Prefer Existing AI Models
Before implementing any AI-related feature, check whether the required capability is already covered by an approved model in Dependencies.txt.
If an approved model exists:
- Download it.
- Integrate it into CHITTI.
- Expose it through the AI Runtime.
- Reuse it everywhere.
Do not implement custom AI logic that duplicates an approved model's purpose.

### Rule 2 — Approved AI Stack
The following models are the official AI stack for CHITTI and must be treated as the default implementation unless there is a documented technical reason otherwise:
- Wake Word: openWakeWord
- Voice Activity Detection: Silero VAD
- Speech Recognition: Faster-Whisper
- Intent Classification: ModernBERT
- Entity Extraction: ModernBERT NER
- Capability Routing: ModernBERT
- Presentation Selection: ModernBERT
- Confidence & Tone: TinyBERT
- Memory Importance: TinyBERT
- Embeddings: BGE Small
- Semantic Search: BGE Small
- Search Ranking: BGE Reranker
- OCR: PaddleOCR
- Vision: SmolVLM-256M
- Planning & Conversation: Gemma 3 1B or Qwen2.5-1.5B
These models are the engineering baseline for CHITTI.

### Rule 3 — Never Reimplement Well-Established AI
Do not write custom implementations for well-established AI capabilities (Intent classification, Entity extraction, Semantic search, OCR, Wake word detection, Speech recognition, Tone detection, Confidence estimation, Presentation selection) already provided by approved models.

### Rule 4 — Write Integration, Not Replacement
AntiGravity is expected to write: Runtime code, Service layer, Model adapters, Provider wrappers, Download manager, Model manager, Caching, Scheduling, Hardware selection, Result normalization, Capability integration, Workflow orchestration.
AntiGravity is not expected to rewrite machine learning algorithms that already exist in approved models.

### Rule 5 — One Model, Many Features
Every model should be reused across the entire project. Never create multiple classifiers if one well-trained model can support all of them.

### Rule 6 — AI Runtime Owns Models
Capabilities must never import model libraries directly. The AI Runtime decides which model executes the request.
Forbidden: `from transformers import AutoModel`, `model.predict(...)`
Required: `intent = IntentService.classify(text)`

### Rule 7 — Document Exceptions
If AntiGravity decides not to use an approved model, it must explain: Why the model is unsuitable, Why a custom implementation is necessary, Why another approved model cannot solve the problem, The expected maintenance cost. Without this justification, the default assumption is that the approved model should be integrated rather than replaced.

### Rule 8 — Approved Models Are Replaceable
The approved AI stack defines the default providers, not permanent implementations. Every approved model must be integrated behind a provider interface so it can be replaced with a superior implementation without changing Capabilities, Workflows, Service APIs, or Runtime interfaces.

### Rule 9 — AI Models Are Dependencies, Not Features
Treat every approved model as an external dependency, similar to SQLite or PySide6. The application's intelligence comes from Models + Architecture + Workflow + Memory + Desktop Automation + Planning = CHITTI. A model alone is not CHITTI, and CHITTI should never depend on one specific model implementation.

### Rule 10 — AI Models Must Be Interchangeable
Every AI provider must be replaceable without modifying Capabilities, Workflows, Services, or the AI Runtime. Replacing ModernBERT with another intent classifier, or Whisper with another speech engine, should require changes only inside the provider adapter and the YAML manifest.

### Rule 11 — AI Models Are Stateless
Every provider invocation must be independent. Never allow providers to track conversation state (`provider.last_intent`, `provider.context`). Conversation and workflow state belongs strictly to the Memory Runtime, Session Runtime, or Workflow Runtime. Providers must remain purely functional, reusable, thread-safe, and stateless.

### Rule 12 — AI Runtime Never Chooses Workflow
The AI Runtime may classify, infer, rank, or generate. It must never decide which capability executes, workflow order, permissions, or automation sequences. Those orchestration responsibilities belong exclusively to the Workflow Runtime, Planner Runtime, and Capability Runtime. This preserves deterministic behavior and prevents LLMs from quietly taking over orchestration.

### Rule 13 — AI Runtime Never Stores State
The AI Runtime itself must never maintain conversation history, user profiles, workflow states, execution history, or memory caches. Those belong to dedicated runtimes (Memory Runtime, Session Runtime, Workflow Runtime). The AI Runtime must remain strictly stateless aside from transient execution.

## Architectural Governance
**Mandate:** No pull request may introduce a new runtime or architectural layer without an approved Architecture Decision Record (ADR).

### Rule 205 — Local First
Always prefer local models when hardware requirements are satisfied.

### Rule 206 — Cloud is a Fallback
Cloud providers are fallback execution providers. Capabilities must never know whether execution occurred locally or in the cloud.

### Rule 207 — Credentials are Secrets
Credentials must never be stored in Memory Runtime, SQLite, Conversation history, or Configuration files. Use Credential Manager exclusively.

### Rule 208 — Cloud Providers Are Replaceable
OpenRouter is the default implementation. The architecture must allow future providers without modifying Workflow Runtime, Planner Runtime, AI Runtime, or Capabilities. Only the Cloud Provider Adapter should change.

### Rule 209 — Commercial Licensing & openWakeWord
The CHITTI stack is completely commercially viable (Apache 2.0 / MIT) with one exception: `openWakeWord` default pre-trained models are CC BY-NC-SA (non-commercial). For any commercial deployment, a custom wake word model MUST be trained using their Apache 2.0 open-source framework to avoid licensing violations.

## Rule 240 – Runtime Prohibition
No new runtime may be introduced unless an ADR demonstrates that its responsibilities cannot reasonably belong to an existing runtime.

## Rule 33 (Revised) – Semantic Runtime produces meaning, never execution
It converts transcripts into normalized, language-independent intents with confidence scores. Selecting capabilities, planning workflows, retries, and execution remain responsibilities of the Runtime Kernel.

## Rule 34 (Revised) – Semantic Runtime Sandbox
Semantic Runtime shall never access capabilities, workflows, memory, planners, or desktop automation. It may only transform transcripts into normalized semantic representations and publish semantic events.

## Rule 35 – Deterministic Planning
The Planner Runtime shall be deterministic. Given the same `DesktopIntent` and the same Capability Registry, it must always generate the same `ExecutionPlan`. Large Language Models may assist only when acquiring previously unknown capabilities through the Adaptive Capability Acquisition pipeline, never during planning of known capabilities.

## Rule 36 – Execution Succeeds Only After Verification
Execution succeeds only after verification. A capability may report that it has finished executing, but the Runtime Kernel must not consider the workflow successful until the Verification Runtime confirms that the intended real-world system state has been achieved.

## Rule 37 – Evidence First Verification
Verification shall always use the lowest-cost evidence source capable of determining system state. Native operating system evidence, Activity Timeline, application APIs, and accessibility data shall be evaluated before OCR or Vision. Vision exists as a verification fallback and for explicit visual requests.

## Rule 38 – Capability Runtime Responsibility
CapabilityRuntime executes exactly one ExecutionStep. It must remain unaware of workflows, planners, retries, dependency graphs, or verification. Workflow orchestration belongs exclusively to the Runtime Kernel and Execution Scheduler.

## Rule 39 – Only Verified Outcomes Become Knowledge
Experience Learning Engine and Adaptive Learning Runtime must consume only `VERIFICATION_COMPLETED` (or equivalent verified-success events), never raw execution-completed events. Execution is an attempt; verification is the proof that the intended outcome actually occurred.

## Rule 40 – Presentation Never Determines Truth
Presentation communicates verified truth. It never determines truth. Verification decides success; Presentation decides how that success is communicated. Personality should never influence planning, reasoning, execution, or verification.

## Rule 41 – Additive Speech
Speech exists only when it adds information beyond what the user can already perceive.

## Rule 42 – Avatar Hierarchy
Avatar is the primary communication channel. The hierarchy is: Animation > Sound > Speech.

## Rule 43 – Minimized Presence
Minimized is not inactive. Edge-docked CHITTI remains fully alive.

## Rule 242 — Inference Independence

The Product, Planner, Conversation Runtime, Behavior Runtime, Workflow Runtime, and Capability Runtime shall remain completely independent of any inference engine, model, provider, quantization, or deployment strategy. Inference providers are replaceable implementation details behind the Provider Registry.

## Rule 243 — Product Experience First

New infrastructure, runtimes, frameworks, abstractions, or platform layers may only be introduced when required by at least three independent product features or when they eliminate a demonstrable architectural limitation. Otherwise, product development shall extend the existing frozen platform through composition.

## Rule 245 — Execution Outcome Truthfulness
AI-generated responses must never fabricate the outcome of deterministic operations. When answering questions about executed workflows (e.g., "Did it close?", "Did the file download?", "Did my build finish?"), the Conversation Runtime must consult the latest `ExecutionContext` or `ExecutionResult` before invoking the AI.

## Rule 246 — Entity Resolution Ownership
ConversationRuntime owns conversational state, entity resolution, and session lifecycle. AIRuntime consumes already-resolved conversational context and must not perform entity resolution or infer deterministic references (e.g., "it", "that file", "the project") independently.

## Rule 247 — Context Providers Are the Only Source of AI Context
AIRuntime must never directly query memory, workspace, execution state, activities, capabilities, or companion state. All contextual information supplied to the AI must originate from registered Context Providers coordinated by the ContextAssembler.

## Rule 248 — Capability Certification Gate
Every capability must formally pass a 7-stage certification gate before release:
1. Intent Resolution (AIRuntime)
2. Planner Resolution (PlannerRuntime)
3. Registry Discovery (PackageManagerRuntime)
4. Execution (ExecutionRuntime)
5. Verification (VerificationRuntime)
6. Conversation Response (ConversationRuntime)
7. Regression Tests (Full Pipeline)

## Rule 249 — Capability Modularity
Every new capability must be independently installable, independently testable, independently verifiable, and removable without affecting the execution spine.

## Rule 250 — RuntimeCapabilityRegistry is Mandatory
No capability may bypass the RuntimeCapabilityRegistry. 

## Rule 251 — No Direct Capability Invocation
No capability may be directly invoked for production validation. All validation must pass through the Execution Spine.

## Rule 252 — Canonical Output Preservation
The ExecutionRuntime SHALL preserve canonical output within its execution payload.

## Rule 253 — ConversationArtifact Immutability
A ConversationArtifact SHALL remain immutable after creation.

## Rule 254 — PresentationDescriptor Separation of Concerns
A PresentationDescriptor SHALL only describe UI. It SHALL NEVER render UI.

## Rule 255 — MemoryCandidate Optionality
A MemoryCandidate SHALL remain optional in capability executions.

## Execution Spine Regression
## Rule 256 — Mandatory Execution Spine Regression
Every capability SHALL pass the Execution Spine regression (test_capability_execution_spine.py) before merge.

## Rule 257 — Evidence-Based Architectural Claims
No architectural assumption shall be accepted as validation evidence. Every architectural claim shall be supported by either repository inspection or observed runtime execution.

## Rule 258 — Mandatory Validation Report Artifacts
Any future Sprint Validation Report must include three mandatory artifacts: Repository Impact Report (design changes), Implementation Report (code changes), and Runtime Evidence Report (actual execution logs).

## Rule 259 — Permanent Engineering Workflow Standard
Beginning with Sprint 31B, every sprint SHALL strictly follow the `CHITTI_ENGINEERING_PROCESS_STANDARD.md` workflow. This mandatory lifecycle includes Planning, Architecture Review, Implementation, Implementation Review, Certification, and Handoff Contract generation. No sprint may begin until the previous sprint is fully certified and frozen. Every review SHALL conclude with the "WHAT'S NEXT" format and an Antigravity prompt.

## Frozen Architecture & Safe Evolution Directive

## Rule 260 — Repository Structure Lock
Repository structure is LOCKED. Never move folders, rename folders, rename canonical modules, reorganize packages, relocate runtimes, or relocate capabilities unless explicitly requested by the project owner.

## Rule 261 — Comprehensive Dependency Analysis
Assume every canonical module has unknown downstream dependencies. Always perform dependency analysis before modifying any existing module.

## Rule 262 — Engineering Priority Escalation
Engineering priorities: 1. Reuse existing -> 2. Extend extension points -> 3. Use adapters -> 4. Use providers -> 5. Use composition -> 6. Minimal canonical module modification -> 7. Repository restructuring ONLY if unavoidable.

## Rule 263 — No Architectural Redesign for Convenience
Never redesign architecture for convenience. Cleanliness is NOT sufficient justification. Existing stable architecture always wins.

## Rule 264 — Refactoring Proof Mandate
Every proposal to move, rename, split, merge, or relocate modules MUST prove measurable benefit, zero regression risk, zero dependency breakage, zero API breakage, and zero runtime breakage. Otherwise, it is automatically rejected.

## Rule 265 — Extension Patterns Over Code Modification
When adding new functionality, prefer Provider, Adapter, Registry, Plugin, Extension, Strategy patterns instead of modifying stable code.

## Rule 266 — Minimal Safe Changes
If modifying an existing module is unavoidable, minimize code changes, preserve public APIs, file paths, contracts, EventBus topics, configuration, and canonical ownership.

## Rule 267 — No Duplicate Implementations
Never create duplicate implementations. Always check Exists, Partially Exists, Missing first. Only implement the missing portion.

## Rule 268 — Standard 8-Step Engineering Pipeline
Every future implementation SHALL follow: Repository Discovery -> Ownership Verification -> Dependency Analysis -> Gap Analysis -> Architecture Safety Review -> Implementation -> Verification -> Certification.

## Rule 269 — Default Structural Freeze
Any proposal that changes repository structure SHALL require explicit approval from the project owner before implementation. Default assumption: REPOSITORY STRUCTURE IS FROZEN.

