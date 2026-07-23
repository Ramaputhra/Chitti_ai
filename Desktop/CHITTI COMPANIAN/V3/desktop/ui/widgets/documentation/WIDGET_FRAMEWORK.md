# CHITTI V2 — DESKTOP WIDGET FRAMEWORK ARCHITECTURE

## 1. Executive Summary
The **Desktop Widget Framework** (`desktop/ui/widgets/`) is the ONLY platform responsible for desktop widgets. It operates as a strict consumer of the Desktop UI Runtime Foundation.

---

## 2. Architecture & Pipeline

```
Runtime Session -> Widget Runtime -> Widget Registry (Category Filter / Version Validator) -> Widget Manager -> Desktop UI Runtime -> Desktop Windows
```

- **Runtime Sessions Only:** Widgets visualize Runtime Sessions ONLY (`WidgetSession`). Capabilities are metadata only.
- **Manifest Versioning & Categories:** Manifest schema `1.0.0`, Widget version `1.0.0`, and 8 canonical categories (`MEDIA`, `COMMUNICATION`, `SYSTEM`, `PRODUCTIVITY`, `AUTOMATION`, `PRESENTATION`, `VISION`, `UTILITY`).
- **No Window Ownership:** Widgets SHALL NEVER create or own windows directly. They request transparent generic windows from the Desktop UI Runtime Foundation.
- **Window Attachment:** Consumes `WindowAttachment` API (`CHARACTER_ANCHOR`, `DESKTOP_COORD`, `SCREEN_EDGE`, `RUNTIME_SESSION`, `MOUSE_POS`). Widgets SHALL NEVER move Character Window directly.
