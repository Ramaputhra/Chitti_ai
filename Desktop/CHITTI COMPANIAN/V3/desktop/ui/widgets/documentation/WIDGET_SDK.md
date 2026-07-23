# CHITTI V2 — WIDGET SDK SPECIFICATION

## 1. Base Class (`BaseWidget`)
Every widget inherits from `BaseWidget` (`desktop/ui/widgets/sdk/widget.py`) and implements:
- `initialize(context)`
- `bind_session(session)`
- `update(delta_data)`
- `render()`
- `expand()`
- `collapse()`
- `dock(edge)`
- `undock()`
- `attach(target_type, anchor_data)`
- `detach()`
- `show()`
- `hide()`
- `close()`
- `destroy()`

---

## 2. Design System Tokens & Styling
- **Corners:** Rounded 10px (`corner_radius_px`)
- **Typography:** Noto Sans, Segoe UI Variable, Noto Sans CJK
- **Shadow:** Soft 32px blur drop shadow
- **Blur:** 16px Glass Blur
- **Borders:** Minimal 1px border (`border_style`)
