# CHITTI V2 — DESKTOP UI RUNTIME FOUNDATION ARCHITECTURE

## 1. Executive Summary
The **Desktop UI Runtime Foundation** (`desktop/ui/`) is the canonical desktop rendering platform for CHITTI. It governs Desktop Windows, Overlays, Notifications, Floating Windows, Dialogs, GPU Accelerated Composition, Motion Token Integration, Layout Engine, Asset Pipeline, Theme System, Window Lifecycle Management, Canonical Window IDs, Semantic Window Layers, and Generic Window Attachment.

---

## 2. Architecture & Pipeline

```
Runtime Session -> Desktop UI Runtime -> Window Manager / Layer Translator / Attachment Engine / Layout Engine -> Desktop Overlay Windows
```

- **Canonical Window IDs:** Every window instance possesses a permanent canonical identifier (`UI_WINDOW_CHARACTER_WIDGET`, `UI_WINDOW_NOTIFICATION`, `UI_WINDOW_DIALOG`, `UI_WINDOW_FLOATING`, `UI_WINDOW_OVERLAY`, etc.).
- **Semantic Window Layers:** Window ordering is governed by semantic layers (`CHARACTER` < `CHARACTER_WIDGET` < `FLOATING_WIDGET` < `NOTIFICATION` < `DIALOG` < `SYSTEM_OVERLAY` < `DEBUG`).
- **Generic Window Attachment:** Windows attach to targets via `WindowAttachment` contract (`CHARACTER_ANCHOR`, `DESKTOP_COORD`, `SCREEN_EDGE`, `MOUSE_POS`, `RUNTIME_SESSION`).
- **Character Platform Integration:** Desktop UI Runtime consumes ONLY the Character Anchor API (`get_character_anchor()`) and Character Runtime Events. It SHALL NEVER move the Character Window or decode Character PNG assets.
- **Motion Integration:** Consumes ONLY Motion Tokens (`desktop/shared/motion/`). No local motion constants or local easing curves permitted.
