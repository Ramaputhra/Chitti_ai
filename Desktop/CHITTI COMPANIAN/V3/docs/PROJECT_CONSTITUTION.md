# Project Constitution

This is the highest authority in the repository. It contains only immutable rules.

1. CHITTI is a Desktop Companion.
2. Companion before Automation.
3. Product-first development.
4. Experience-first sprints.
5. Local-first AI.
6. Privacy-first.
7. Human always in control.
8. Archive instead of delete.
9. One architecture.
10. One roadmap.
11. One product.
12. Every sprint delivers a complete user experience.
13. Architecture changes require explicit approval.
14. Blueprint overrides historical sprint decisions.
15. The repository exists to ship a product—not to explore architecture.
16. **Temporal Rule**: CHITTI never thinks in terms of "timers", "alarms", or "monitoring" as separate systems. Every future action that waits for a point in time or a condition must be represented as a `ScheduledEvent` managed by the `TimeRuntime`. New waiting mechanisms must extend this model rather than creating parallel implementations.
17. **Context Provider Rule**: Context Providers produce deterministic evidence. Evidence must be correlated and compressed before entering Memory. Semantic interpretation belongs exclusively to higher cognitive layers (Memory, Embeddings, Planner) and never to Context Providers.
22. **Provider-Agnostic Composition Rule**: Context Providers must emit provider-specific evidence only. EpisodeBuilder is the sole component responsible for constructing provider-agnostic WORK_SESSION episodes. Context Providers must never write directly to Memory or perform cross-provider aggregation.
23. **Shared Evaluation Rule**: Shared evaluation logic must remain provider-independent. Algorithms that rank, score, compress, or summarize evidence belong to shared evaluators, not individual Context Providers.
24. **Provider Independence Rule**: Context Providers must be independently executable and testable. A provider shall depend only on shared evidence models and provider interfaces.
25. **Provider Data Minimization Rule**: Context Providers must minimize retained evidence. Providers should collect only the smallest deterministic representation necessary for cognition. Large payloads, binary data, and sensitive content must be summarized, hashed, or redacted before entering the Evidence Pipeline.
26. **Realtime Observation Rule**: Context Providers observe user interaction, not operating-system history. Providers must prioritize evidence generated during the active WorkSession. Historical operating-system artifacts shall be implemented as separate providers or enrichment sources and must never replace realtime session evidence.
27. **Identity Normalization Rule**: Shared identity resolution belongs to dedicated resolver services. Context Providers may observe raw resources, but normalization into reusable identities must be delegated to shared resolvers to ensure consistent cognition across all providers.
28. **Safe Restoration Rule**: Context Providers must observe user intent without performing actions. Restore capabilities may reconstruct environment state (windows, folders, working directories, browser sessions), but they must never automatically replay user actions, execute commands, or modify external systems without explicit Planner authorization and user confirmation.
29. **Deterministic Resolution Rule**: Shared identity resolution must be deterministic, local-first, and reusable. Resolvers may inspect local system state required for normalization (such as filesystem structure), but they must never perform semantic inference, background indexing, or provider-specific reasoning. Multiple Context Providers should resolve identical resources into the same Identity instance whenever possible.
30. **Canonical Identity Rule**: Identities are canonical. Every real-world entity (project, workspace, repository, document, command, resource) must resolve to a single canonical Identity. Context Providers may observe different representations of the same entity, but Resolvers must normalize them so higher cognitive layers reason about one shared object rather than duplicate representations.
31. **Canonical Synthesis Rule**: Cross-provider synthesis must operate exclusively on canonical identities. EpisodeBuilder and higher aggregation layers may merge evidence only when providers resolve to the same canonical Identity. They must never infer equivalence through labels, window titles, or semantic similarity.
32. **Deterministic Workflow Reconstruction Rule**: Workflow reconstruction must remain deterministic. Workflow reconstruction may sequence, classify, and relate observed events using timestamps, canonical identities, and deterministic metadata, but it must never infer user goals, intentions, or semantic meaning. Goal inference belongs exclusively to higher cognitive layers (Planner and Memory).
33. **Deterministic Outcome Assessment Rule**: Outcome extraction may classify workflow completion, validation state, and execution results using deterministic workflow patterns and observable evidence. It must never infer user intent, project semantics, or business meaning. Those belong exclusively to higher cognitive layers.
34. **Evidence-Driven Intent Modeling Rule**: Intent modeling must remain evidence-driven. Intent extraction may propose one or more deterministic intent candidates derived from workflow outcomes and supporting evidence, but it must never select a primary intent, infer project semantics, or establish user goals. Final intent selection belongs exclusively to the Planner.
35. **Planner Authority Rule**: The Planner is the sole component authorized to establish an active goal or user intent. Deterministic components may reconstruct history, assess outcomes, and propose intent candidates, but they must never resolve ambiguity or claim final understanding.
36. **Goal Continuity Rule**: Goal continuity must be evidence-driven. A goal may continue, pause, complete, or be abandoned only through observable continuity between current reasoning context and previously established goals. The Planner must never assume abandonment solely because a new goal has appeared.
37. **Product Delivery Rule**: Every sprint after Sprint 133 must conclude with at least one complete, user-visible capability that can be demonstrated end-to-end from the CHITTI application. Architectural work alone is no longer sufficient to complete a sprint.

***
**ARCHITECTURE FREEZE: Perception & Cognition Framework (Rules 41–56 in AGENT.md)**
The vertical slice spanning deterministic observation, workflow reconstruction, outcome assessment, intent extraction, goal selection, and goal continuity is officially **FROZEN**. No new layers or abstractions should be added to this framework. Future work must consume this foundation to deliver user-facing companion capabilities rather than redesigning the infrastructure.
***
