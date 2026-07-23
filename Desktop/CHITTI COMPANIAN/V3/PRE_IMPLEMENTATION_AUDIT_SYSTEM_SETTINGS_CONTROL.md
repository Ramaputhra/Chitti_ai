# CHITTI V2 — MANDATORY PRE-IMPLEMENTATION ENGINEERING AUDIT
**(FEATURE: SYSTEM_SETTINGS_CONTROL)**

======================================================================
## 1. EXECUTIVE SUMMARY
======================================================================

A mandatory, non-destructive pre-implementation engineering audit was conducted for the proposed **`SYSTEM_SETTINGS_CONTROL`** feature (OS Master Volume, Audio Mute, Display Brightness, and OS Power State Controls).

### Audit Findings:
- **Feature Exists in Repository?** **PARTIALLY IMPLEMENTED.** Native Win32 key simulation for volume keys (`VK_VOLUME_UP`, `VK_VOLUME_DOWN`, `VK_VOLUME_MUTE`) already exists in `MediaControlCapability` (`desktop/capabilities/desktop/media_control.py`). Direct OS audio endpoint volume query and display brightness controls are missing.
- **Canonical Owner:** `DesktopCapability` / `MediaControlCapability` (`desktop/capabilities/desktop/`).
- **New Capability Package Required?** **NO.** Creating a new package is **PROHIBITED**. This feature SHALL extend existing modules under `desktop/capabilities/desktop/`.
- **Frozen Platform Impact:** **ZERO IMPACT TO FROZEN PLATFORMS.**

---

======================================================================
## 2. PHASE 1 — FEATURE DISCOVERY & REPOSITORY AUDIT
======================================================================

An exhaustive search across the entire repository was performed:

1. **`desktop/capabilities/desktop/media_control.py`:**
   - Contains `MediaControlCapability` executing Win32 multimedia virtual keys (`VK_MEDIA_PLAY_PAUSE`, `VK_MEDIA_NEXT_TRACK`, `VK_MEDIA_PREV_TRACK`, `VK_VOLUME_MUTE`, `VK_VOLUME_DOWN`, `VK_VOLUME_UP`).
2. **`desktop/capabilities/desktop/automation/drivers.py`:**
   - Contains Win32 desktop automation drivers for keyboard input and window management.
3. **`desktop/platform/observation/sources.py`:**
   - Contains `DesktopSource` capturing primary display resolution and monitor layouts.

---

======================================================================
## 3. PHASE 2 — CAPABILITY OWNERSHIP & CANONICAL MAPPING
======================================================================

- **Canonical Capability Owner:** `MediaControlCapability` & `DesktopAutomationCapability`
- **Repository Path:** `desktop/capabilities/desktop/`
- **Owner Runtime:** `CapabilityRuntime` (`desktop/runtimes/capability/`)
- **Owner Platform:** Capability Platform (`desktop/capabilities/`)
- **Existing APIs:** `describe()`, `execute()`, `health_check()`, `state()`.
- **Sprint Origin:** Sprint 22 / EPIC 36.

---

======================================================================
## 4. PHASE 3 — DEPENDENCY ANALYSIS
======================================================================

- **Modules Consuming This Feature:** `WorkflowRuntime`, `CapabilityRegistry`, `VisualCoordinator`, `Media` Widget.
- **Modules Consumed By This Feature:** Win32 API (`ctypes.windll.user32`), `EventBus`, `BaseCapability`.
- **Runtime Dependencies:** `CapabilityRuntime`.
- **EventBus Dependencies:** Emits `CapabilityExecuted` upon execution.
- **UI / Widget Dependencies:** `System` & `Media` Desktop Widgets (30 FPS).
- **Voice / Character Dependencies:** `VoiceRuntime` speaks narration confirmation; `CharacterRuntime` animates slime mascot (14 FPS).
- **Frozen Platform Impact:** **ZERO IMPACT TO FROZEN PLATFORMS.** Character Platform, Desktop UI Runtime Foundation, Motion Design System, and Cognitive Core V1 remain 100% untouched.

---

======================================================================
## 5. PHASE 4 — IMPLEMENTATION STATUS
======================================================================

- **Classification:** **PARTIALLY IMPLEMENTED (60%)**
- **Existing Implementation:** Win32 virtual key press events for volume up, volume down, and mute toggle.
- **Missing Implementation:** Explicit percent-level audio volume setter/getter (e.g. "Set volume to 50%"), display brightness adjustment API, and power state request (Lock, Sleep).

---

======================================================================
## 6. PHASE 5 — GAP ANALYSIS
======================================================================

### Already Exists (Reusable Components):
- `MediaControlCapability` facade (`desktop/capabilities/desktop/media_control.py`).
- Tool descriptors (`play_pause`, `next_track`, `volume_up`, `volume_down`, `mute`).
- Win32 Virtual Key dispatcher.

### Missing Components (The Only Code To Be Added):
- Submodule `system_settings.py` inside `desktop/capabilities/desktop/` adding:
  - `set_volume_percent(percent: int)` via Windows Endpoint Volume API / WinMM.
  - `get_volume_percent() -> int`.
  - `set_brightness_percent(percent: int)` via Win32 WMI / Monitor API.
  - `lock_workstation()` via Win32 `LockWorkStation`.

---

======================================================================
## 7. PHASE 6 — IMPACT ANALYSIS
======================================================================

- **Character Platform:** NO modification.
- **Desktop UI Runtime Foundation:** NO modification.
- **Widget Framework:** NO modification.
- **Visual Coordinator Platform:** NO modification.
- **Planner & Workflow Spine:** NO modification.
- **Memory & Verification Engines:** NO modification.

### Statement of Safety:
**ZERO IMPACT TO FROZEN PLATFORMS.**

---

======================================================================
## 8. PHASE 7 — MINIMAL IMPLEMENTATION PLAN
======================================================================

### Files to Modify / Extend:
1. `desktop/capabilities/desktop/media_control.py` (Extend tool descriptors to include `set_volume`, `get_volume`, `lock_screen`).

### Files to Create (Minimal):
1. `desktop/capabilities/desktop/system_settings.py` (Submodule implementing pure Win32 helper functions for volume percentage and lock workstation).
2. `tests/capabilities/test_system_settings.py` (Verification unit tests).

### Documentation & Verification Updates:
- Update `CAPABILITY_CATALOG.md`.
- Run verification test `python tests/capabilities/test_system_settings.py`.

### Regression Risk: **LOW**

---

======================================================================
## 9. PHASE 8 — ENGINEERING DECISION
======================================================================

1. **Does this feature already exist?** **PARTIAL (60% Implemented)**
2. **Who is the canonical owner?** `desktop/capabilities/desktop/` (`MediaControlCapability`)
3. **Can the feature be implemented by extending existing modules?** **YES**
4. **Is creating a new capability package prohibited?** **YES**
5. **Will frozen platforms remain untouched?** **YES**
6. **Estimated implementation effort:** **Small**
7. **Risk Level:** **LOW**

---

======================================================================
## 10. FINAL DECISION
======================================================================

```
######################################################################
                  FINAL PRE-IMPLEMENTATION DECISION

                            DECISION:
                      APPROVED FOR EXTENSION

   The SYSTEM_SETTINGS_CONTROL feature SHALL be implemented strictly by
   extending existing modules under desktop/capabilities/desktop/
   without creating any new top-level capability package.

   All frozen platforms remain 100% protected.
######################################################################
```
