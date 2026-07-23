# CHITTI Platform Specification
**The Constitution of CHITTI**

This document serves as the master architectural reference for CHITTI, a desktop AI platform. It defines the identity, core components, and invariant principles governing the platform's evolution.

---

## 1. Project Identity

### Mission
To build a highly capable, contextually aware desktop AI companion that seamlessly integrates into the user's workflow without causing disruption or friction.

### Vision
A deterministic-first platform where AI enhances execution but does not dictate it. CHITTI acts as an invisible collaborator until actively needed or when proactively delivering immense value.

### Design Goals
- **Decoupled Architecture**: Absolute separation between what CHITTI decides to do (Logic), how CHITTI does it (Execution), and how CHITTI communicates it (Behavior/Personality).
- **Determinism**: Workflows must be predictable, replayable, and safe.
- **Contextual Awareness**: Real-time awareness of the desktop environment without continuous polling.
- **Proactive Modularity**: Experiences run independently of the core conversational loop.

### Non-goals
- Over-reliance on LLMs for control flow, logic, or execution graphs.
- Undocumented, opaque, or non-deterministic capabilities.
- Mixing state and UI into monolithic runtimes.

### Product Principles (Companion Philosophy)
- Silence is better than unnecessary narration.
- Personality must never block execution.
- LLM enhances; it never controls deterministic operations.
- Every interaction should reduce friction for the user.
- CHITTI behaves as a companion, not merely a command executor.

---

## 2. Runtime Dependency Graph

```text
Speech
    ↓
Intent
    ↓
Workflow
    ↓
Planner
    ↓
Execution Graph
    ↓
Scheduler
    ↓
Execution
    ↓
Capabilities

────────────

Presence
    ↓
Experience
    ↓
Workflow

────────────

Behavior
    ↓
Emotion
    ↓
Narration
    ↓
Character
    ↓
Expression
    ↓
TTS
```

---

## 3. Runtime Responsibilities Matrix

| Runtime | Owns | Never Does |
| :--- | :--- | :--- |
| **Intent** | Understanding user goals | Execution |
| **Workflow** | Logical step definitions | Scheduling |
| **Planner** | Capability selection | Execution |
| **Scheduler** | Execution order & resource locks | Business logic |
| **Execution** | Running capability nodes safely | Personality/Behavior generation |
| **Character** | Dialogue and persona generation | TTS rendering |
| **Experience** | Triggering proactive workflows | Narration or direct capability execution |

---

## 4. Storage Architecture

Persistent storage is highly localized and cleanly owned by distinct runtimes.

| Store | Location | Owner Runtime | Purpose |
| :--- | :--- | :--- | :--- |
| **Config** | `.gemini/config/` | System Kernel | Bootstrapping core platform variables |
| **Profile** | `AppData/CHITTI/profile/` | Profile Runtime | WHO the user is (Identity, Voice, Experience toggles) |
| **Settings** | `AppData/CHITTI/settings/` | Settings Runtime | HOW CHITTI behaves (Theme, FPS, Logging) |
| **Memory** | `AppData/CHITTI/memory/` | Memory Runtime | Short/Long-term recall (via IMemoryIndex) |
| **Journal** | `AppData/CHITTI/journal/` | Memory/Context | Time-series interaction history |
| **Knowledge** | `AppData/CHITTI/knowledge/` | Knowledge Runtime | Persistent facts, RAG indices, project contexts |
| **Workspace** | `AppData/CHITTI/workspaces/`| Workspace Runtime | Definitions for layouts, apps, and window positions |
| **Plugins** | `AppData/CHITTI/plugins/` | Plugin Sandbox | 3rd-party code and manifests |
| **Cache** | `AppData/CHITTI/cache/` | System Kernel | Transient data |
| **Models** | `AppData/CHITTI/models/` | Model/Compute | Local AI weights/loras |
| **Logs** | `AppData/CHITTI/logs/` | Logger | System tracing and telemetry |

---

## 5. AI Architecture

CHITTI utilizes AI, but restricts its authority.

```text
Deterministic First
        ↓
Rule Engine (Eligibility, Triggers)
        ↓
Knowledge Retrieval (RAG, Context)
        ↓
LLM (Summarization, Dialogue, Intent Mapping)
        ↓
Learning (Feedback ingestion)
        ↓
Promotion (To permanent rules or memory)
```
**Golden Rule of AI in CHITTI:** The LLM is an advanced capability provider. It receives structured `LLMRequest` objects from the platform. It does not dictate system state, control the scheduler, or directly interact with the file system.

---

## 6. Extension Points

CHITTI is designed for growth through the following extension points:
- **Capabilities:** Atomic, deterministic python scripts (e.g., `sys.file.open`) mapped to intents.
- **Experiences:** Proactive workflows triggered by presence/system states, utilizing modular `IExperienceSectionProvider`s.
- **Skills:** Bundled capabilities and knowledge targeting a specific domain.
- **Plugins:** Sandboxed 3rd-party capabilities (Upcoming in Phase 8).
- **Presentation Runtime:** Interactive visual session manager (Architecturally Frozen for Phase 9).

---

## 7. Engineering Rules

Development on CHITTI is governed by a strict set of rules defined in `AGENTS.md`. 
The most critical rule defining the frozen state of this platform is **Rule 264**.

### Rule 264 – Runtime Stability
> Certified runtimes are considered stable platform components. New product features must not expand their responsibilities. Additional functionality should be implemented through capabilities, providers, experiences, skills, or plugins unless the runtime's core contract itself requires revision.

### Rule 265 – Presentation Isolation
> Presentation Runtime owns visualization only. It must never perform exports, file operations, printing, communication, or browser automation directly. All user actions (Export, Save, Print, Email, WhatsApp, Share, Close, etc.) are translated into deterministic Presentation Intents and executed exclusively through the standard Intent → Workflow → Scheduler → Execution pipeline. Presentation Sessions remain fully lifecycle-managed, observable, and independently testable.

### Rule 266 – Presentation Context Ownership
> The Presentation Runtime is the sole owner of the active Presentation Context. No other runtime may infer, mutate, or directly access browser state. All presentation interactions must occur through Presentation Intents and Presentation Events.

### Rule 267 — Knowledge is Immutable by Default
> Knowledge records are append-first. Existing facts should not be silently overwritten. Updates create new revisions or supersede previous records, preserving history unless explicit deletion is requested.

### Rule 268 — The Knowledge Runtime Never Infers
> The Knowledge Runtime stores, indexes, retrieves, versions, and validates knowledge. It must never infer new facts. Inference belongs exclusively to the Reasoning/Inference Runtime or LLM layer.

### Rule 269 — Knowledge Must Be Traceable
> Every persisted knowledge record must retain its origin, creation time, revision history, and supporting source reference. No knowledge may exist without provenance.

### Rule 270 — Retrieval Must Be Deterministic
> Given the same `KnowledgeQuery` and unchanged knowledge state, the Knowledge Runtime must return the same ordered result set. Ranking algorithms must remain deterministic unless explicitly configured otherwise.

### Rule 271 — Knowledge Providers are Pure Collectors
> Knowledge Providers are pure collectors. They normalize external information into Knowledge models but never validate, persist, infer, or publish knowledge independently.

### Rule 272 — Knowledge Collection Initiator
> Knowledge collection is always initiated by the Knowledge Runtime. Providers never autonomously inject knowledge into the platform.

### Rule 273 — Capabilities are Discoverable, Not Hardcoded
> No runtime may directly invoke a capability by implementation class. All executable functionality must be resolved dynamically through the Service Registry.

### Rule 274 — Skills Orchestrate, Capabilities Execute
> Skills orchestrate capabilities but never implement business logic themselves. Business logic belongs exclusively to Capabilities.

### Rule 275 — Plugin Constraints
> Plugins extend the registry only. They never modify Planner, Scheduler, Behavior, or Knowledge runtimes directly.

### Rule 276 — Universal Service Registration
> Every executable component in CHITTI must be registered before it can participate in planning or execution. Unregistered services are invisible to the platform.

### Rule 277 — Deterministic Planner Selection
> The Planner must select services through deterministic registry queries. Direct references to implementation classes are prohibited.

### Rule 278 — Registry Separation
> Registry entries are declarative metadata only. They never execute code or instantiate implementations.

### Rule 279 — Plugin Isolation
> Plugins never receive direct references to core runtimes. All interactions occur through stable platform APIs and declarative service registration.

### Rule 280 — Resource Governance
> Plugin execution is sandboxed and resource-governed. Plugins cannot bypass Scheduler, Execution Supervisor, Policy Runtime, or Resource Manager.

### Rule 281 — Event Ownership
> A plugin cannot publish privileged system events directly. Security-sensitive events remain exclusively owned by their respective core runtimes.

### Rule 282 — Reserved Namespaces
> Core namespaces (e.g. system.*, knowledge.*, execution.*) are reserved. Third-party plugins may not override, replace, or shadow built-in platform services.

### Rule 283 — API Versioning
> Platform APIs are versioned contracts. Plugins target API versions, not runtime implementations.

### Rule 284 — No Internal Imports
> Plugins communicate exclusively through Platform APIs and declarative service registration. Reflection, runtime monkey-patching, and direct imports of internal runtime modules are prohibited.

### Rule 285 — Stateless Plugins
> Plugins are stateless between invocations.

### Rule 286 — Read-Only Retrieval
> Retrieval never modifies knowledge. It is read-only.

### Rule 287 — Isolated Ranking
> Retrieval providers never rank globally. They return candidate results only. Global ranking belongs exclusively to Ranking Engine.

### Rule 288 — Immutable Context
> Context packages are immutable. No runtime modifies retrieved context after construction.

### Rule 289 — Isolated Storage Access
> LLMs never directly query storage. All retrieval passes through Retrieval Runtime.

### Rule 290 — Async Embeddings

> Embedding generation is asynchronous. Never block execution.

### Rule 291 — Retrieval is Explainable
> Every retrieved item must carry provenance describing the provider, source, score, and ranking reason.

### Rule 292 — Provider Independence
> Retrieval providers must never call one another. Only Retrieval Runtime orchestrates providers.

### Rule 293 — Reasoning decides. Planner orchestrates.
> The Reasoning Runtime produces the deterministic plan. The Planner executes that sequence.

### Rule 294 — LLMs are Optional
> LLMs are optional participants, never mandatory. Reasoning decides if they are required.

### Rule 295 — Explainable Reasoning
> Every decision contains a structured trace explaining exactly why retrieval, AI, execution, or presentation was selected.

### Rule 296 — Reasoning Never Executes
> Reasoning Runtime may inspect context and services, but it never executes capabilities.

### Rule 297 — Reasoning Never Retrieves Directly
> Reasoning consumes the immutable ContextPackage. It never bypasses the Retrieval Runtime to fetch data.

### Rule 298 — Reasoning Never Calls LLMs Directly
> Reasoning determines if AI is needed; the AI Gateway owns actual model invocation.

### Rule 299 — Planner Trusts ReasoningPlan
> Planner must not reinterpret reasoning policies. It blindly orchestrates the resulting ReasoningPlan.

### Rule 300 — Composition Declaration
> Capabilities declare compatibility; Composer determines composition.

### Rule 301 — Successor Ignorance
> Capabilities never know their successors. (e.g. PDF capability should never know Email exists).

### Rule 302 — Declarative Workflows
> Workflows are declarative products of composition.

### Rule 303 — Planner Isolation
> Planner never searches for capabilities. Planner receives an already-composed WorkflowBlueprint.

### Rule 304 — Composer Determinism
> For a given ReasoningPlan, Registry, Context, and Policy, the Composer always generates identical output.

### Rule 305 — Workflow Validation
> Every WorkflowBlueprint must pass structural validation before it reaches the Planner.

### Rule 306 — Service Compatibility
> Service compatibility is declared exclusively through metadata, never implementation code inspection.

### Rule 307 — Package Isolation
> Packages never modify the platform directly. They register components. Nothing else.

### Rule 308 — Lifecycle Separation
> Installation and activation are separate operations. Installing does not mean running.

### Rule 309 — Version Independence
> Every package is versioned independently. Core platform updates must not require package updates.

### Rule 310 — Declarative Dependencies
> Package dependencies are declarative. No package manually installs another package.

### Rule 311 — Safe Uninstallation
> Every installed package must be removable without damaging the platform.

### Rule 312 — No Giant Packages
> Packages define features. Bundles group packages. Packages do not group unrelated features.

### Rule 313 — Components Register Through Owning Runtime
> A package is a distribution container, not an execution unit. Components are registered strictly through the runtime that owns their domain. Package Manager only routes.

### Rule 314 — Platform Evolution
> New functionality must enter the platform through registration, composition, and package installation. Core runtimes remain unchanged. Any feature requiring modification of stable core runtimes represents an architectural regression and must undergo an Architecture Impact Review.

### Rule 315 — Presentation Synchronization Ownership
> The Presentation Runtime owns the readiness of a presentation session. The Behavior Runtime never inspects renderer state. Narration begins only after receiving an explicit synchronization-ready event from the Presentation Runtime or after a bounded timeout, ensuring deterministic synchronization without cross-runtime coupling.

### Rule 316 — Persistent UI Contexts
> A Presentation Session owns the user's visual context independently of the renderer. Renderers may disconnect, reconnect, or migrate without destroying the session. User interactions, selections, filters, and navigation belong to the session, not to the rendering engine.

### Rule 317 — Local UI Interaction
> Presentation interactions that affect only visual state (selection, scrolling, zooming, filtering, tab changes, layout adjustments) are handled exclusively within the Presentation Session Runtime. Only interactions that request platform functionality (export, save, print, share, refresh, execute, close, etc.) are elevated into Presentation Intents and routed through the standard Intent → Reasoning → Composer → Planner → Execution pipeline.

### Rule 318 — Presentation Model Immutability
> PresentationModels are immutable after publication. Any visual change must be represented as a new PresentationModel or a generated PresentationPatch produced exclusively by the Presentation Runtime. Capabilities, Skills, and Plugins must never mutate active PresentationModels directly.

### Rule 319 — Renderer Idempotency
> Renderers must treat PresentationCommands as idempotent. Receiving the same command more than once must not duplicate UI state or produce inconsistent visual behavior. Commands are uniquely identified by `command_id` and `model_version`.

### Rule 320 — Protocol Stability
> The Frontend Protocol is a public platform contract. Once a protocol version is released, future platform versions must preserve backward compatibility or provide explicit protocol version negotiation. Internal Presentation Runtime changes must never silently break existing frontends.

### Rule 321 — Transport Agnosticism
> Presentation Runtimes and Renderers must communicate exclusively through the Frontend Protocol. They must never depend on WebSockets, HTTP, IPC, or any specific transport implementation. Transports are interchangeable infrastructure components beneath the protocol layer.

### Rule 322 — Frontend Runtime Isolation
> React components are visual only. They must never implement protocol parsing, session management, transport logic, or workflow behavior. All frontend application logic belongs exclusively to the Frontend Runtime layer.

### Rule 323 — Template Purity
> Presentation Templates are pure visual adapters. They must never communicate with the backend, mutate session state, invoke workflows, or parse protocol messages. All interaction occurs exclusively through the Frontend Runtime layer.

### Rule 324 — Widget Composition
> Presentation Templates compose Widgets. They must never implement business visualization internally. Charts, Tables, Galleries, Timelines, Markdown viewers, and Cards are independent widgets registered through the Widget Registry.

### Rule 325 — Widgets are Stateless Renderers
> Persistent UI state belongs exclusively to PresentationSessionRuntime. Widgets render the provided state and emit interactions but never persist user context internally.

### Rule 326 — Widgets communicate exclusively through WidgetAction and WidgetPatch.
> Widgets never communicate directly with each other.

### Rule 327 — Widget state belongs exclusively to WidgetStateRuntime.
> Widgets do not own state.

### Rule 328 — Local UI interactions never invoke platform execution unless promoted by the WidgetActionRouter.
> Local interactions stay local. Only the Action Router decides when to emit intent over the network.

### Rule 329 — Presentation widgets remain deterministic and stateless.
> UI components are pure visual functions over the data and state provided by the session.

### Rule 330 — Widget actions are immutable.
> Once emitted, WidgetActions are never modified. Routing decisions create new actions or patches rather than mutating the original event.

### Rule 331 — Frontend runtimes own interaction logic.
> Widgets remain pure visual emitters. All business, interaction, and state logic is strictly handled by the Frontend Runtimes.

### Rule 332 — Widgets declare capabilities; layouts compose widgets.
> Layouts structure space, widgets provide visual capabilities.

### Rule 333 — Layouts never render business logic.
> Layouts are generic wrappers.

### Rule 334 — Widgets must remain package-installable without frontend modification.
> Adding a widget is a data-driven registration.

### Rule 335 — Widget rendering must remain deterministic for identical PresentationModels.
> A layout + state model always produces the same visual output.

### Rule 336 — Widget packages may extend the Widget Registry but never PresentationSessionRuntime.
> The runtime is secure and sealed.

### Rule 337 — Widgets consume standardized datasets rather than arbitrary dictionaries.
> Dataset validation occurs before rendering.

### Rule 338 — Themes, skins, icons, layouts, animations, and widgets are independently package-installable components.
> The Presentation Engine is an ecosystem.

### Rule 339 — Component compatibility must be validated before registration.
> Version matrices and dependencies must be satisfied.

### Rule 340 — Presentation history consists of immutable snapshots and must never be modified after capture.
> Enables playback and historical queries.

### Rule 341 — Presentation Experiences define user-facing workflows. Recipes transform structured data into PresentationModels.
> Experiences dictate what is shown; Recipes dictate how data becomes that view.

### Rule 342 — Recipes are deterministic transformers. They never execute capabilities or query storage.
> Recipes are pure functions over PresentationExperienceContext.

### Rule 343 — Experience replay restores immutable snapshots without re-executing workflows.
> No capability execution, no retrieval, no AI—just rendering a past model.

### Rule 344 — Experiences remain package-installable through the Presentation Experience Registry.
> They are dynamic and discoverable.

### Rule 345 — Experiences are Stateless.
> The Experience implementation itself should never store user state. State belongs exclusively to PresentationMemory + PresentationSession.

### Rule 346 — Runtime Owns Concurrency.
> Experiences should never launch their own threads or async tasks. Only ExperienceRuntime controls streaming, cancellation, and background updates.

### Rule 347 — Experience Infrastructure Freeze
> Core Presentation and Experience infrastructure may not be expanded after Sprint 9.9 unless the Architecture Impact Review demonstrates that the capability cannot be implemented as an Experience, Recipe, Widget, Layout, Theme, Runtime Extension, or Package.

### Rule 348 — Environment Isolation
> Adapters communicate exclusively through the Environment Runtime. They never invoke Planner, Scheduler, Presentation, or Behavior directly.

### Rule 349 — Environment Sessions
> Long-running environment interactions are represented as EnvironmentSessions owned by the Environment Runtime.

### Rule 350 — Adapter Capability Declaration
> Adapters expose declarative capabilities. Execution decisions are based on capabilities, never implementation classes.

### Rule 351 — Resource Arbitration
> Environment resources are acquired through the Runtime. Adapters never perform independent locking or scheduling.

### Rule 352 — Generic Actions
> EnvironmentActions remain environment-neutral. Adapters translate generic actions into native operations.

### Rule 353 — Adapter Statelessness
> Adapters must remain stateless translators. Persistent execution state belongs exclusively to the EnvironmentSession. Adapters may cache transient implementation details but must never become the source of truth for workflow state.

### Rule 354 — Adapter Engine Independence
> Environment Adapters translate generic platform actions. Native automation libraries (Playwright, Selenium, Win32, Appium, etc.) are implementation details hidden behind engine interfaces and must never leak beyond the adapter boundary.

### Rule 355 — Environment Object Abstraction
> Environment adapters must expose normalized platform objects (for example BrowserElementReference or DesktopObjectReference). Native engine objects (Playwright Locator, Win32 HWND, UIAutomationElement, etc.) must never cross the adapter boundary.

### Rule 356 — Resources are Stable References
> EnvironmentResources represent stable logical objects. Adapters may translate them into native engine objects, but native engine objects must never escape the Environment Platform.

### Rule 357 — IDE Engine Independence
> IDE adapters communicate exclusively through IIDEEngine. Native IDE APIs, Language Server Protocol implementations, or editor SDKs must never leak outside the engine boundary.

### Rule 358 — Workspace Ownership
> IDE sessions own workspace state. Engines never persist project state.

### Rule 359 — Developer Resources are Abstract
> Files, editors, terminals, symbols, diagnostics, and breakpoints are represented by normalized platform models rather than IDE-native objects.

### Rule 360 — Communication Independence
> Communication adapters expose normalized communication resources. They never expose provider SDKs.

### Rule 361 — Provider Isolation
> SMTP, Gmail API, Microsoft Graph, Google Calendar, REST APIs, Exchange, etc. remain hidden behind Engine interfaces.

### Rule 362 — Communication Sessions
> Long-running conversations, inbox synchronization, subscriptions and API authentication belong to Communication Sessions, never Engines.

### Rule 363 — Messages are Resources
> Messages, events, API responses and invitations are EnvironmentResources.

### Rule 364 — Adapter Contract Compliance
> Every Environment Adapter must implement the complete IEnvironmentAdapter contract. Partial implementations are not production-ready.

### Rule 365 — Environment Capability Declaration
> Every Adapter must explicitly declare every supported EnvironmentCapability. Capabilities may never infer adapter functionality.

### Rule 366 — Cross-Environment Consistency
> All adapters must expose identical lifecycle semantics (Session, Resource, Action, Result, Artifact, Telemetry, Recovery) regardless of implementation.

### Rule 367 — Environment Platform Freeze
> After certification, Browser, Desktop, File, IDE, and Communication infrastructure becomes frozen. Future expansion occurs only through Adapters, Engines, Capability Packs, Packages, or Plugins.

*For a complete list of rules, see `.agents/AGENTS.md`.*

---

## Architecture Impact Review

Before adding any new runtime to CHITTI, a mandatory 6-point Architecture Impact Review must be passed:
1. **Ownership** – Does another runtime already own this responsibility?
2. **Boundary** – Does it violate any Engineering Rules or layer separation?
3. **Dependencies** – Does it introduce cycles or hidden coupling?
4. **Abstraction** – Could this be a Capability, Provider, Plugin, or Service instead of a Runtime?
5. **Performance** – What are the startup, memory, latency, and concurrency impacts?
6. **Observability** – Can every decision and state transition be traced and explained?

---

## 8. Version Roadmap

  - Interactive Presentation Sessions (Lifecycle, Inactivity Engine)
  - Widget Registry & Incremental Updates (`PresentationPatch`)
  - Browser Independence (Presentation Host → Browser Provider → Renderer)
  - Presentation Memory & History
  - Presentation Intents (SHARE, EXPORT, UPDATE)
- **Phase 10:** Agentic Automation
