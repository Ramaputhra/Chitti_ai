# CHITTI V2 — CHARACTER IDENTITY PLATFORM ARCHITECTURE

## 1. Executive Summary
The **Character Identity Platform** (`desktop/character/identity/`) serves as the single canonical knowledge base for Character Name, Identity, Biography, Mission, Philosophy, Beliefs, Creator Information, Speech Rules, Self Knowledge, Capabilities, Limitations, and Canonical Self Responses.

---

## 2. Platform Architecture & Separation
```
User -> Intent Classifier -> Identity Capability -> Identity Runtime -> Identity Context -> LLM -> Narration Composer -> Voice Runtime -> SpeechTimeline -> Behavior Scheduler -> Character Runtime
```

- **Canonical Character Knowledge Base:** Identity Platform is a pure authored knowledge source.
- **No Engine / Wake Configuration:** Identity Platform contains ZERO engine, runtime, or wake configuration fields (`wake_names`, `wake_phrases`, `wakeword`). Wake Runtime remains the ONLY owner of wake configuration.
- **LLM Grounding Rule:** The LLM NEVER invents identity facts. All identity queries are strictly grounded in authored Markdown & JSON documents inside `desktop/character/identity/profiles/`.
- **Live Hot Reload:** Any edits to Markdown identity documents trigger automatic live reloading without platform restart.
