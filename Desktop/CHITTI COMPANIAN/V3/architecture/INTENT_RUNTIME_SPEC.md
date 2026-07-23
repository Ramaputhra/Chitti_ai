# Intent Runtime Specification
> **1. The architecture must remain deterministic by default. AI reasoning is an optional capability, never a mandatory dependency for system operation. Any feature that can be executed through deterministic logic must not require an LLM.**
>
> **2. Every runtime must be independently testable, restartable, and replaceable without requiring changes to unrelated runtimes.**
>
> **5. Every runtime, planner, scheduler, and capability must exist only to improve the AI Desktop Companion experience. Architectural complexity must always provide measurable product value.**

## 1. Purpose
Transforms normalized natural language text (`SpeechTranscribed` events or direct text input) into structured, typed, language-independent intents. It serves as CHITTI's primary comprehension engine, isolating semantic interpretation from execution.

## 2. Responsibilities
- **JSON-Driven Configurations:** Relies strictly on `desktop/config/` for `intents/`, `normalization/`, `entities/`, and `clarifications.json`. Python code handles algorithms; JSON handles data.
- **Hot Reloading:** The registry supports reloading configurations at runtime without application restart.
- **Immutable Intent IDs:** Intent IDs (e.g., `OPEN_APPLICATION`) are strictly immutable and never change regardless of pattern or language evolution.
- **Text Normalization:** Uses a JSON-backed Normalization Dictionary to convert multilingual and colloquial expressions into canonical tokens (e.g., standardizing "Chrome open chey" or "బ్రౌజర్ తెరువు" to "browser open").
- **Deterministic First (Local Intent Registry):** Attempt to match canonical text to an intent using an ultra-fast, local, rule-based registry without an LLM.
- **Threshold-Gated Routing:** Uses strict confidence thresholds:
  - `HIGH (>= 0.95)`: Immediate deterministic execution.
  - `MEDIUM (0.75 - 0.94)`: Emits `IntentClarificationRequired` pulling from `clarifications.json`. LLM fallback is prevented.
  - `LOW (< 0.75)`: Triggers LLM inference for semantic matching. If still LOW, emits `IntentUnknown`.
- **Entity Extraction & Resolution:** Extracts raw entities (e.g., "browser") and explicitly resolves them to concrete resources (e.g., "chrome.exe").
- **Entity Validation:** The resolver verifies if the concrete resource actually exists (e.g., is Chrome installed?). If not, it falls back or returns `EntityNotFound`.
- **Intent Validation:** An explicit final validation stage runs before emitting events to ensure all required entities and metadata are complete.
- **Intent Statistics (Telemetry):** Emits lightweight statistics (confidence, duration_ms, source, language) for every recognition loop to enable future analytics.
- **Language Independence:** Identical user goals produce the exact same canonical intent identifier, regardless of spoken language.
- **Pronoun Resolution:** Consumes lightweight Conversation Context from the Context Runtime to resolve references like "it" or "that".

## 3. Intent Organization
- **Intent Categories:** Every intent belongs to a logical group (e.g., `System`, `Files`, `Browser`, `Media`, `Communication`, `Conversation`).
- **Intent Metadata:** Exposes strict declarative metadata (e.g., `requires_confirmation`, `requires_authentication`, `supports_background`, `supports_parallel`) allowing the Policy Engine and Planner to make decisions dynamically.

## 4. Interfaces
- **Inputs:** `SpeechTranscribed`, `TextInputReceived`, `ConversationContext`.
- **Outputs:** Emits `IntentRecognized`, `IntentClarificationRequired`, or `IntentUnknown`.
- **API:** Implement `IRuntime`.

## 5. Events
- `IntentRecognized`
  ```yaml
  intent_id: "OPEN_APPLICATION"
  category: "System"
  metadata:
    requires_authentication: true
    requires_confirmation: false
  entities: 
    app_name: "chrome.exe"
  confidence: 0.98
  source: "core_registry" 
  ```
- `IntentClarificationRequired`
- `IntentUnknown`

## 6. Dependencies
- EventBus
- Local Intent Registry & Normalization Dictionary
- Context Runtime (for lightweight conversation context)
- AI Gateway (for LLM fallback on LOW confidence)

## 7. Failure Modes
- If AI Gateway is offline and local registry misses, emit `IntentUnknown` for the Character Runtime to request clarification gracefully.

## 8. Lifecycle
Follows standard `IRuntime` strict state machine. During `INITIALIZING`, it loads the versioned Local Intent Registry (Core Intents, User Intents, Learned Intents) and the Normalization Dictionary into memory.

## 9. Future Extensions
- Few-shot semantic similarity matching using local embedding models.

## 10. Out of Scope
- **Execution:** The Intent Runtime **never** executes tasks, opens apps, or plans steps. It only declares *what* the user wants. 
- **Self-Learning:** The Intent Runtime is strictly read-only. Updates to the Learned Intents registry are delegated to the Experience Runtime after successful execution and user confirmation.

## Acceptance Criteria

□ Purpose is defined
□ Responsibilities are complete
□ Interfaces are documented
□ Events are documented
□ Dependencies are identified
□ Failure modes are defined
□ Lifecycle is complete
□ Future extensions are identified
□ Out-of-scope boundaries are defined
□ Version 1 / Version 2 / Final Architecture comparison is complete
