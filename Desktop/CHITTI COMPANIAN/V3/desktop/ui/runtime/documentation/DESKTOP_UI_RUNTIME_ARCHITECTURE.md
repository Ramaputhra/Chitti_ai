# CHITTI V2 — DESKTOP UI RUNTIME ARCHITECTURE

## 1. Executive Summary
The **Desktop UI Runtime & Widget Framework** (`desktop/ui/runtime/`) is the ONLY runtime responsible for rendering Desktop Notifications, Toasts, Dialogs, Floating Windows, Countdowns, Badges, Widgets, Docked Widgets, Character Attached Widgets, and Overlay Windows.

---

## 2. Architecture & Pipeline
```
Capability Runtime -> Runtime Session -> Desktop UI Runtime -> Overlay / Notification / Widget / Window / Docking Managers -> Desktop Overlay Windows
```

- **Strict Rendering Responsibility:** Desktop UI Runtime NEVER executes capabilities. It ONLY visualizes runtime sessions.
- **Event-Driven Isolation:** Exposes ONLY events to the future `Visual Coordinator` (Sprint S36E). Does NOT communicate directly with Character Runtime, Presentation Runtime, or Voice Runtime.
