# CHITTI V2 — VISUAL COORDINATOR PLATFORM ARCHITECTURE

## 1. Executive Summary
The **Visual Coordinator Platform** (`desktop/coordinator/`) is the canonical orchestration platform for CHITTI. It synchronizes visual behavior across Character Runtime, Voice Runtime, Desktop UI Runtime, Desktop Widget Framework, Presentation Runtime, and Execution Runtime without introducing direct dependencies between them.

---

## 2. Architecture & Pipeline

```
Runtime Session -> Visual Coordinator (Timeline Scheduler / Priority Engine / Conflict Resolver) -> Published Runtime Contracts -> Character / Voice / Desktop UI / Widgets
```

- **Single Source of Timing Truth:** Merges Speech, Character, Widget, Presentation, Notification, and Execution Timelines into a Unified Timeline.
- **Zero Rendering & Zero Capability Execution:** Visual Coordinator SHALL NEVER render UI, create windows, execute capabilities, or own UI assets.
- **Canonical Visual States:** `Speaking`, `Listening`, `Thinking`, `Working`, `Presenting`, `Downloading`, `Printing`, `Idle`, `Sleeping`, `Busy`, `Background`, `Presentation`, `Fullscreen`.
- **Fault Tolerance:** If one runtime crashes, Recovery Manager recovers and resynchronizes remaining runtimes cleanly without restarting CHITTI.
