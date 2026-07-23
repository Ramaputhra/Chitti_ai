# Runtime Data Flow Architecture

The following diagram defines the critical path for a user request in the CHITTI system.

- Memory is an **on-demand service**, not a bottleneck.
- The Planner is bypassed for simple intents to maximize speed.
- The Skill Dispatcher triggers the appropriate action.

```mermaid
graph TD
    V[Voice] --> STT[Speech-To-Text]
    STT --> CE[Conversation Engine]
    CE --> CtxE[Context Engine]
    
    CtxE --> IE[Intent Engine]
    CtxE --> MS[Memory Service]
    IE -. requests memory if needed .-> MS
    
    IE --> IR{Intent Resolved}
    
    IR -->|Simple| SD[Skill Dispatcher]
    IR -->|Complex| P[Planner]
    P --> TP[Task Pipeline]
    TP --> SD
    
    SD --> EE[Emotion Engine]
    EE --> RG[Response Generator]
    RG --> MW[Memory Writer]
    MW --> TTS[TTS]
```
