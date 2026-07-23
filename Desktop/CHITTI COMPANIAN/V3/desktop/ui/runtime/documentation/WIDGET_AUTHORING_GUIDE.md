# CHITTI V2 — WIDGET AUTHORING GUIDE

Welcome to the **CHITTI V2 Widget Authoring Guide**. This document explains how to author new desktop widgets that bind to runtime sessions.

---

## 1. Widget Contract (`BaseWidget`)
Every widget must inherit from `BaseWidget` (`desktop/ui/runtime/widgets/base_widget.py`) and implement:
- `initialize()`
- `bind_session(session)`
- `update(delta_data)`
- `render()`
- `expand()`
- `collapse()`
- `dock(mode)`
- `undock()`
- `close()`
- `destroy()`

---

## 2. Generic Widget Catalog (17 Types)
`Media`, `Reminder`, `Alarm`, `Email`, `Browser`, `Navigation`, `Presentation`, `Printer`, `Download`, `Upload`, `Vision`, `Clipboard`, `Battery`, `Weather`, `Productivity`, `System`, `Timer`.
