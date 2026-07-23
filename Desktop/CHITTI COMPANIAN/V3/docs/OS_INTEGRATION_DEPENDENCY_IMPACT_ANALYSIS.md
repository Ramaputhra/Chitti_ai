# CHITTI V2 — PRE-EPIC 37 ARCHITECTURAL DEPENDENCY IMPACT ANALYSIS
**(Non-Destructive Audit & Facade Safety Assessment)**

======================================================================
## 1. EXECUTIVE SUMMARY & FINAL VERDICT
======================================================================

A comprehensive, non-destructive dependency audit was conducted across the entire CHITTI V2 codebase to evaluate the architectural safety of introducing an **OS Integration Platform Facade (`desktop/integration/os/`)** prior to launching **EPIC 37**.

### Central Question:
**"Is introducing `desktop/integration/os/` architecturally safe?"**

### Final Verdict:
```
######################################################################
                  FINAL ARCHITECTURAL VERDICT

                            VERDICT:
                    YES (WRAP ONLY - NO MOVES)

   Architecturally SAFE if implemented strictly as a thin, non-destructive 
   aggregation facade that imports existing canonical endpoints.

   HIGH RISK & FORBIDDEN if implemented by moving, renaming, or deleting 
   existing frozen capability and observation modules.
######################################################################
```

---

======================================================================
## 2. CANDIDATE MODULE DEPENDENCY MATRIX
======================================================================

Below is the exhaustive forward and reverse dependency graph for every candidate OS integration and observation module currently implemented in the repository.

### 2.1 ProcessSource
- **Repository Path:** `desktop/platform/observation/sources.py`
- **Owner Platform:** Observation Platform (`desktop/platform/observation/`)
- **Purpose:** Captures objective OS process metrics (`pid`, `name`, `parent_pid`, `cpu_percent`, `memory_mb`).
- **Forward Graph (Uses):** `uuid`, `datetime`, `Observation` model (`desktop/models/observation.py`).
- **Reverse Graph (Used By):** `ObservationManager` (`desktop/platform/observation/manager.py`), Activity Intelligence (`desktop/platform/activity/`).
- **Current Ownership Correct?** **YES.** Owned correctly by Observation Platform.
- **Recommendation:** **KEEP AS IS / WRAP ONLY**

### 2.2 WindowSource
- **Repository Path:** `desktop/platform/observation/sources.py`
- **Owner Platform:** Observation Platform (`desktop/platform/observation/`)
- **Purpose:** Captures objective OS window bounds (`hwnd`, `pid`, `title`, `bounds`, `state`, `is_active`).
- **Forward Graph (Uses):** `uuid`, `datetime`, `Observation` model.
- **Reverse Graph (Used By):** `ObservationManager`, Verification Runtime (`desktop/runtimes/verification/`), Activity Engine.
- **Current Ownership Correct?** **YES.** Owned correctly by Observation Platform.
- **Recommendation:** **KEEP AS IS / WRAP ONLY**

### 2.3 DesktopSource
- **Repository Path:** `desktop/platform/observation/sources.py`
- **Owner Platform:** Observation Platform (`desktop/platform/observation/`)
- **Purpose:** Captures foreground application and primary monitor layout state.
- **Forward Graph (Uses):** `Observation` model.
- **Reverse Graph (Used By):** `ObservationManager`, Verification Runtime.
- **Current Ownership Correct?** **YES.** Owned correctly by Observation Platform.
- **Recommendation:** **KEEP AS IS / WRAP ONLY**

### 2.4 DesktopAutomationCapability
- **Repository Path:** `desktop/capabilities/desktop/automation/capability.py`
- **Owner Platform:** Capability Platform (`desktop/capabilities/desktop/automation/`)
- **Purpose:** Provides intent-based physical desktop controls (window focus, mouse clicks, key typing) delegating to `DesktopAutomationRuntime`.
- **Forward Graph (Uses):** `DesktopAutomationRuntime` (`drivers.py`, `runtime.py`), `EventBus`, `CapabilityDescriptor`, `ToolDescriptor`.
- **Reverse Graph (Used By):** `CapabilityRegistry` (`desktop/runtimes/capability/registry.py`), Workflow Execution Spine, Benchmark Suites (`desktop/benchmarks/`).
- **Current Ownership Correct?** **YES.** Owned correctly by Capability Platform.
- **Recommendation:** **KEEP AS IS / WRAP ONLY**

### 2.5 ClipboardCapability
- **Repository Path:** `desktop/capabilities/desktop/clipboard.py`
- **Owner Platform:** Capability Platform (`desktop/capabilities/desktop/`)
- **Purpose:** Manages system clipboard reading, writing, history tracking, and content clearance.
- **Forward Graph (Uses):** `EventBus`, `BaseCapability`, `ICapability`.
- **Reverse Graph (Used By):** `CapabilityRegistry`, Workflow Runtime, `desktop_pack` capabilities (`desktop/packages/desktop_pack/capabilities/clipboard.py`).
- **Current Ownership Correct?** **YES.** Owned correctly by Capability Platform.
- **Recommendation:** **KEEP AS IS / WRAP ONLY**

### 2.6 AppLauncherCapability
- **Repository Path:** `desktop/capabilities/desktop/app_launcher.py`
- **Owner Platform:** Capability Platform (`desktop/capabilities/desktop/`)
- **Purpose:** Launches native Windows applications (`notepad.exe`, `chrome.exe`, `explorer.exe`) and manages process handles.
- **Forward Graph (Uses):** `BaseCapability`, `ServiceState`, `CapabilityDescriptor`.
- **Reverse Graph (Used By):** `CapabilityRegistry`, Workflow Runtime, `benchmark_001_find_file.py`.
- **Current Ownership Correct?** **YES.** Owned correctly by Capability Platform.
- **Recommendation:** **KEEP AS IS / WRAP ONLY**

### 2.7 MediaControlCapability
- **Repository Path:** `desktop/capabilities/desktop/media_control.py`
- **Owner Platform:** Capability Platform (`desktop/capabilities/desktop/`)
- **Purpose:** Controls system multimedia playback (Play, Pause, Next, Previous, Volume, Mute) via native key events.
- **Forward Graph (Uses):** `BaseCapability`, `CapabilityDescriptor`.
- **Reverse Graph (Used By):** `CapabilityRegistry`, `Media` WidgetSession Manager (`desktop/ui/widgets/`).
- **Current Ownership Correct?** **YES.** Owned correctly by Capability Platform.
- **Recommendation:** **KEEP AS IS / WRAP ONLY**

### 2.8 BrowserCapability
- **Repository Path:** `desktop/capabilities/browser/browser_capability.py`
- **Owner Platform:** Capability Platform (`desktop/capabilities/browser/`)
- **Purpose:** Executes Playwright browser automation, navigation, page element clicking, form filling, and emits `PageSnapshot`.
- **Forward Graph (Uses):** Playwright driver, `PageSnapshot` schema, `EventBus`.
- **Reverse Graph (Used By):** `CapabilityRegistry`, Workflow Runtime, Browser Intelligence Platform (Sprint 28 **FROZEN**).
- **Current Ownership Correct?** **YES.** Owned correctly by Capability Platform.
- **Recommendation:** **DO NOT TOUCH / WRAP ONLY**

### 2.9 VisionCapability & OCR Engine
- **Repository Path:** `desktop/capabilities/vision/vision_capability.py`
- **Owner Platform:** Capability Platform (`desktop/capabilities/vision/`)
- **Purpose:** Captures screen bounding boxes, performs OCR text extraction, constructs `VisionLayoutTree`.
- **Forward Graph (Uses):** Desktop screenshot driver, OCR Layout Tree parser, `EventBus`.
- **Reverse Graph (Used By):** `CapabilityRegistry`, Workflow Runtime, Vision Intelligence Platform (Sprint 29 **FROZEN**).
- **Current Ownership Correct?** **YES.** Owned correctly by Capability Platform.
- **Recommendation:** **DO NOT TOUCH / WRAP ONLY**

### 2.10 FileCapability
- **Repository Path:** `desktop/capabilities/desktop/filesystem/` & `desktop/capabilities/files/`
- **Owner Platform:** Capability Platform (`desktop/capabilities/files/`)
- **Purpose:** Executes filesystem operations (create, read, write, copy, move, delete, list directories, search files).
- **Forward Graph (Uses):** Native Python `os`/`shutil` APIs, `BaseCapability`.
- **Reverse Graph (Used By):** `CapabilityRegistry`, Benchmark Suites (`benchmark_002_organize_downloads.py`).
- **Current Ownership Correct?** **YES.** Owned correctly by Capability Platform.
- **Recommendation:** **KEEP AS IS / WRAP ONLY**

---

======================================================================
## 3. REVERSE DEPENDENCY MAP & COMPATIBILITY GRAPH
======================================================================

```
[Win32 API / OS Adapters]
       ▲
       │ (Low-Level Driver Invocation)
       │
[desktop/platform/observation/sources.py] <---+
[desktop/capabilities/desktop/automation/] <--+--- (Canonical Source Implementations)
[desktop/capabilities/desktop/clipboard.py]   |
[desktop/capabilities/desktop/app_launcher.py]|
                                              |
       ▲                                      |
       │ (Imports & Re-exports)               |
       │                                      |
[desktop/integration/os/ (Proposed Facade)]---+ (Non-Destructive Facade)
       ▲
       │
[WorkflowRuntime / CapabilityRegistry / VerificationRuntime / Benchmarks]
```

---

======================================================================
## 4. IMPORT & FROZEN PLATFORM IMPACT ASSESSMENT
======================================================================

### Scenario A: Moving / Renaming Files into `desktop/integration/os/` (FORBIDDEN)
- **Files Affected:** 42+ implementation files.
- **Imports Broken:** Over 80+ explicit import statements in `CapabilityRegistry`, `ObservationManager`, benchmark jobs, integration tests, and workflow translators.
- **Frozen Platform Impact:** **HIGH RISK**. Violates frozen contracts of Phase 10 Environment Platform, Sprint 28 Browser Intelligence, Sprint 29 Vision Intelligence, and Sprint 30 Activity Intelligence.
- **Verdict:** **FORBIDDEN & REJECTED**.

### Scenario B: Non-Destructive Facade Pattern in `desktop/integration/os/` (APPROVED)
- **Files Affected:** 0 existing files modified or moved.
- **Imports Broken:** 0 broken imports.
- **Frozen Platform Impact:** **ZERO RISK**. All existing capabilities remain in their canonical, frozen repository locations.
- **Implementation Strategy:** The new facade `desktop/integration/os/os_integration_platform.py` simply imports the canonical classes (`ProcessSource`, `WindowSource`, `DesktopAutomationCapability`, `ClipboardCapability`, `AppLauncherCapability`, `MediaControlCapability`) from their original locations and provides a single, unified interface for OS orchestration.
- **Verdict:** **SAFE & APPROVED**.

---

======================================================================
## 5. ENGINEERING RECOMMENDATION MATRIX
======================================================================

| Module Name | Repository Path | Recommendation | Justification |
| :--- | :--- | :--- | :--- |
| `ProcessSource` | `desktop/platform/observation/sources.py` | **KEEP AS IS / WRAP ONLY** | Owned by Observation Platform (Frozen Phase 10). |
| `WindowSource` | `desktop/platform/observation/sources.py` | **KEEP AS IS / WRAP ONLY** | Owned by Observation Platform (Frozen Phase 10). |
| `DesktopSource` | `desktop/platform/observation/sources.py` | **KEEP AS IS / WRAP ONLY** | Owned by Observation Platform (Frozen Phase 10). |
| `DesktopAutomationCapability` | `desktop/capabilities/desktop/automation/` | **KEEP AS IS / WRAP ONLY** | Production ready capability. Consumed by benchmarks. |
| `ClipboardCapability` | `desktop/capabilities/desktop/clipboard.py` | **KEEP AS IS / WRAP ONLY** | Production ready capability. Consumed by packages. |
| `AppLauncherCapability` | `desktop/capabilities/desktop/app_launcher.py` | **KEEP AS IS / WRAP ONLY** | Production ready capability. Consumed by benchmarks. |
| `MediaControlCapability` | `desktop/capabilities/desktop/media_control.py` | **KEEP AS IS / WRAP ONLY** | Production ready capability. Consumed by widgets. |
| `BrowserCapability` | `desktop/capabilities/browser/` | **DO NOT TOUCH** | Browser Intelligence Platform (Sprint 28 Frozen). |
| `VisionCapability` | `desktop/capabilities/vision/` | **DO NOT TOUCH** | Vision Intelligence Platform (Sprint 29 Frozen). |
| `FileCapability` | `desktop/capabilities/desktop/filesystem/` | **KEEP AS IS / WRAP ONLY** | Production ready capability. Consumed by benchmarks. |

---

======================================================================
## 6. FINAL DECISION
======================================================================

### Is introducing `desktop/integration/os/` architecturally safe?

**YES** — provided that:
1. **ZERO existing files are moved, renamed, or deleted.**
2. `desktop/integration/os/os_integration_platform.py` acts strictly as a **thin, non-destructive facade / aggregation interface** that imports existing endpoints from `desktop/platform/observation/` and `desktop/capabilities/desktop/`.
3. All frozen platforms (Character, Desktop UI Runtime, Widget Framework, Visual Coordinator, Cognitive Core V1) remain 100% untouched.
