# CHITTI V2 — MANDATORY PRE-IMPLEMENTATION ENGINEERING AUDIT
**(EPIC 38 — WAVE 1 — SPRINT W1S2-B: OS CONTROL & INTEGRATION)**

======================================================================
## 1. EXECUTIVE SUMMARY
======================================================================

A mandatory, non-destructive pre-implementation engineering audit was conducted for **EPIC 38 — WAVE 1 — SPRINT W1S2-B: OS CONTROL & INTEGRATION** (Process Kill/Suspend/Resume/Restart, Application Activation, Open Folder/Location, Notification & Telemetry Routing, Planner Integration).

### Key Audit Finding:
**Operating System Control & Notification Routing Infrastructure ALREADY PARTIALLY EXISTS (80% Complete).**
The repository already contains `DesktopAutomationCapability` (`desktop/capabilities/desktop/automation/capability.py`), `WindowRuntime` (`runtime.py`), `ProcessSource` (`desktop/platform/observation/sources.py`), `HealthMonitor` (`desktop/platform/integrations/core/health_monitor.py`), `ChannelRuntime` (`desktop/runtimes/channel/channel_runtime.py`), and `OutputRouter` (`router/output.py`).

Creating duplicate control capabilities or new communication packages is **STRICTLY PROHIBITED**. Implementation in Sprint W1S2-B SHALL consist solely of extending the existing `WindowRuntime` and `DesktopAutomationCapability`.

---

======================================================================
## 2. PHASE 1 — REPOSITORY DISCOVERY
======================================================================

Exhaustive repository search revealed the following pre-existing modules:

1. **`desktop/capabilities/desktop/automation/capability.py` & `runtime.py`:**
   - `DesktopAutomationCapability`: Tools for `launch`, `type_text`, `hotkey`, `mouse_click`, `wait`, `close_window`.
   - `WindowRuntime`: Manages `open()`, `activate()`, `close()` via `subprocess` and Windows APIs.
2. **`desktop/platform/observation/sources.py`:**
   - `ProcessSource`: Process classification, application activity mapping, PID/memory/CPU state.
3. **`desktop/platform/integrations/core/health_monitor.py`:**
   - `HealthMonitor`: Live system metrics, resource attribution, smart proactive alerts.
4. **`desktop/runtimes/channel/router/output.py`:**
   - `OutputRouter`: Priority notification routing (`INFO`, `SUCCESS`, `WARNING`, `ERROR`, `CRITICAL`, `PROGRESS`, `ACTION_REQUIRED`) and task timeline streaming.

---

======================================================================
## 3. PHASE 2 — OWNERSHIP VERIFICATION
======================================================================

- **Canonical Owner:** `DesktopAutomationCapability` & `ChannelRuntime`
- **Repository Path:** `desktop/capabilities/desktop/automation/` & `desktop/runtimes/channel/`
- **Owner Platform:** Desktop Automation & Channel Communication Platform
- **Owner Runtime:** `DesktopAutomationRuntime` & `ChannelRuntime`
- **Existing APIs:** `open()`, `activate()`, `close()`, `route_output()`, `send_priority_notification()`, `stream_task_timeline_event()`.

---

======================================================================
## 4. PHASE 3 — DEPENDENCY ANALYSIS & IMPACT REPORT
======================================================================

- **Interacts With:**
  - `psutil` system library: `Process(pid).terminate()`, `suspend()`, `resume()`.
  - `subprocess.Popen`: `explorer.exe /select,"<path>"` for opening folder locations.
  - `EventBus`: Publishes process control execution events.
  - `PlannerRuntime`: Consumes resource-aware application state observations.
- **Frozen Platform Impact:** **ZERO IMPACT TO FROZEN PLATFORMS.** Character Platform, Desktop UI Runtime Foundation, Motion Design System, and Cognitive Core V1 remain 100% untouched.

---

======================================================================
## 5. PHASE 4 — IMPLEMENTATION STATUS
======================================================================

- **Classification:** **PARTIALLY IMPLEMENTED (80% Complete)**
- **Already Implemented (80%):** App launching (`launch`), window closing (`close_window`), process activity mapping (`ProcessSource`), priority notification routing (`OutputRouter`), telemetry streaming (`WebSocketTransport`).
- **Partially Implemented (15%):** Process control (closing window exists, needing direct `kill_process`, `suspend_process`, `resume_process`), File Explorer integration (`launch` works, needing `open_folder` and `open_file_location`).
- **Missing (5%):** `restart_process` tool, render-aware planner context provider wrapper.

---

======================================================================
## 6. PHASE 5 — GAP ANALYSIS & REUSABLE MODULES
======================================================================

### Already Exists & Reusable (80%):
- `DesktopAutomationCapability` & `WindowRuntime` (`desktop/capabilities/desktop/automation/`)
- `ProcessSource` (`desktop/platform/observation/sources.py`)
- `HealthMonitor` (`desktop/platform/integrations/core/health_monitor.py`)
- `OutputRouter` (`desktop/runtimes/channel/router/output.py`)

### Missing Gap To Extend in Sprint W1S2-B (20%):
1. **`WindowRuntime` Extensions:** Add methods `kill(pid)`, `suspend(pid)`, `resume(pid)`, `open_folder(path)`, `open_file_location(filepath)`.
2. **`DesktopAutomationCapability` Tools:** Expose new tools: `kill_process`, `suspend_process`, `resume_process`, `restart_process`, `activate_window`, `open_folder`, `open_file_location`, `system_diagnostics`.

---

======================================================================
## 7. PHASE 6 — ARCHITECTURE SAFETY ASSESSMENT
======================================================================

- **Extension Points:** `DesktopAutomationCapability.discover_tools()` and `_handle_action()` provide standard capability extension points.
- **Adapter Safety:** `WindowRuntime` acts as the underlying OS driver adapter.
- **Zero Frozen Platform Regressions:** All changes are strictly contained within `desktop/capabilities/desktop/automation/`.

---

======================================================================
## 8. PHASE 7 — IMPLEMENTATION READINESS & DECISION
======================================================================

```
######################################################################
                  FINAL PRE-IMPLEMENTATION DECISION

                            DECISION:
                      APPROVED FOR EXTENSION

   The OS_CONTROL_AND_INTEGRATION feature SHALL be implemented strictly by
   extending existing WindowRuntime (runtime.py) and DesktopAutomationCapability
   (desktop/capabilities/desktop/automation/capability.py).

   All frozen platforms remain 100% protected.
######################################################################
```
