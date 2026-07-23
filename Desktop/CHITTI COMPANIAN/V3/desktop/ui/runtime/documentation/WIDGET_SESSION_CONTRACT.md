# CHITTI V2 — WIDGET SESSION CONTRACT

## 1. Overview
Widgets bind to runtime sessions (`UISession`).

```
Runtime Session (Media / Reminder / Presentation / Download) -> UISession -> BaseWidget -> Desktop Overlay
```

- **Lifecycle Synchronization:** When a runtime session completes or terminates, the bound widget automatically closes and disappears.
- **Zero Capability Code:** Widgets contain no action logic; they reflect real-time session state passed via `session.data`.
