# CHITTI V2 — SEMANTIC WINDOW LAYER MODEL

## 1. Executive Summary
The **Semantic Window Layer System** (`window_layers.py`) decouples Desktop UI Z-ordering from operating system specific APIs. Window ordering is governed by canonical semantic layers.

---

## 2. Canonical Layers (Bottom to Top)

1. `CHARACTER` (Priority 100): Base Character Companion Window.
2. `CHARACTER_WIDGET` (Priority 200): Widgets docked to or anchored beside Character.
3. `FLOATING_WIDGET` (Priority 300): Free-floating desktop widgets.
4. `NOTIFICATION` (Priority 400): Desktop toast notifications.
5. `DIALOG` (Priority 500): Modal and non-modal popup dialogs.
6. `SYSTEM_OVERLAY` (Priority 600): Fullscreen overlays, HUDs, and system panels.
7. `DEBUG` (Priority 700): Debug overlays (active during Debug Mode only).

---

## 3. Mandatory Layer Ordering Rules
- **Character Window** is ALWAYS below Character Widgets.
- **Character Widgets** are ALWAYS below Dialogs.
- **Dialogs** are ALWAYS below System Overlays.
- **Debug Windows** are ALWAYS topmost during Debug Mode only.
