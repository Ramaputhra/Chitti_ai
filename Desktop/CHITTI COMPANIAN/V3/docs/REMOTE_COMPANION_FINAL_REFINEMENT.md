# CHITTI V2 — REMOTE COMPANION FINAL MICRO REFINEMENT ANALYSIS
**(WAVE 1 — SPRINT 1: FEATURE: REMOTE_COMPANION)**

======================================================================
## 1. EXECUTIVE SUMMARY
======================================================================

Following the capability enhancement analysis (`REMOTE_COMPANION_ENHANCEMENT_ANALYSIS.md`), five micro refinements were evaluated for **WAVE 1 — SPRINT 1: REMOTE_COMPANION**.

### Core Directive:
- **Canonical Implementation:** `ChannelRuntime` (`desktop/runtimes/channel/`).
- **Architecture Freeze Protection:** Character Platform, Desktop UI Runtime Foundation, Motion Design System, and Cognitive Core V1 remain **100% FROZEN and UNTOUCHED**.
- **Assessment Verdict:** All 5 micro refinements represent **SAFE EXTENSIONS** that can be included in Sprint 1 without architectural modifications or regressions.

---

======================================================================
## 2. REFINEMENT EVALUATION & IMPLEMENTATION MATRIX
======================================================================

| # | Micro Refinement Area | Repository Status | Owner Runtime | Target Files to Extend | Frozen Platform Impact | Priority |
| :-: | :--- | :--- | :--- | :--- | :--- | :-: |
| **1** | **Device Management** | **Safe Extension** | `PairingService` | `desktop/runtimes/channel/models/core.py`<br>`desktop/runtimes/channel/pairing/service.py` | **ZERO** | **High** |
| **2** | **Companion Presence** | **Safe Extension** | `ChannelRouter` | `desktop/runtimes/channel/router/output.py`<br>`frontend/remote_mobile/index.html` | **ZERO** | **High** |
| **3** | **Task Timeline Stream**| **Safe Extension** | `ChannelRouter` | `desktop/runtimes/channel/router/output.py` | **ZERO** | **High** |
| **4** | **Notification Policy** | **Safe Extension** | `ChannelRouter` | `desktop/runtimes/channel/router/output.py` | **ZERO** | **Medium**|
| **5** | **Connection Resilience**| **Safe Extension** | Mobile Web UI | `frontend/remote_mobile/index.html` | **ZERO** | **High** |

---

======================================================================
## 3. DETAILED MICRO REFINEMENT SPECIFICATIONS
======================================================================

### 3.1 Refinement 1 — Device Management
- **Description:** Enhance `TrustedDevice` dataclass (`desktop/runtimes/channel/models/core.py`) with device metadata fields:
  - `device_name`: Friendly string (e.g., "Smile's Galaxy S24").
  - `device_type`: Enum (`PHONE`, `TABLET`, `DESKTOP_CLIENT`).
  - `last_seen`: UTC Timestamp.
  - `pair_date`: UTC Timestamp.
  - `last_ip`: String IPv4/IPv6 address.
  - `trust_revoked`: Boolean flag.
- **Service Extension:** Add `revoke_device(device_id)` and `forget_device(device_id)` methods to `PairingService` (`desktop/runtimes/channel/pairing/service.py`).
- **Impact:** ZERO impact to character or UI runtimes.

### 3.2 Refinement 2 — Companion Presence State Synchronization
- **Description:** Broadcast canonical visual state string (`Listening`, `Thinking`, `Speaking`, `Working`, `Presenting`, `Idle`, `Sleeping`, `Busy`) from `VisualCoordinator` over EventBus into `ChannelRouter.output`.
- **Data Flow:** `VisualStateChanged` $\rightarrow$ `ChannelRouter` $\rightarrow$ WebSocket JSON payload $\rightarrow$ Mobile UI Header Avatar Badge.
- **Safety Guarantee:** Pure JSON data payload synchronization. Character Runtime PNG rendering is **NOT** executed or called.

### 3.3 Refinement 3 — Task Timeline Stream
- **Description:** `ChannelRouter.output` streams structured task progress events to the mobile client rather than raw plain text only.
- **Payload Schema:**
  ```json
  {
    "event_type": "TASK_TIMELINE_UPDATE",
    "task_id": "task_1024",
    "status": "WORKING",
    "progress_percent": 65,
    "current_step": "Searching web for Mamachi",
    "eta_seconds": 3,
    "verification_status": "PASSED"
  }
  ```
- **Impact:** Provides real-time execution visibility on mobile.

### 3.4 Refinement 4 — Notification Policy Mapping
- **Description:** Map EventBus priority levels to mobile notification urgency channels:
  - `CRITICAL` (1000) $\rightarrow$ `CRITICAL` alert toast (Action Required modal).
  - `ERROR` (900) $\rightarrow$ `IMPORTANT` alert toast.
  - `WARNING` (800) $\rightarrow$ `WARNING` toast.
  - `ACTIVE_CONVERSATION` (700) $\rightarrow$ `PROGRESS` update toast.
  - `BACKGROUND` / `IDLE` $\rightarrow$ `SILENT` background notification.
- **Impact:** Keeps mobile notifications structured and non-intrusive.

### 3.5 Refinement 5 — Mobile Web UI Connection Resilience
- **Description:** Single-page mobile web app (`frontend/remote_mobile/index.html`) handles network switches gracefully:
  - **Auto Reconnect:** Re-initiates WebSocket connection using exponential backoff (`1s`, `2s`, `4s`, `8s`, max `16s`).
  - **Session Resume:** Passes saved `permanent_token` during WebSocket handshake.
  - **Offline Banner:** Displays a subtle top banner ("Reconnecting to CHITTI...") when Wi-Fi drops.
  - **Heartbeat Indicator:** Green/Yellow/Red pulse dot showing latency and connection health.
- **Safety Guarantee:** Modifies HTML/JS frontend only; `WebSocketTransport` backend architecture remains untouched.

---

======================================================================
## 4. FINAL RECOMMENDATION
======================================================================

```
######################################################################
                FINAL REFINEMENT RECOMMENDATION

   ALL 5 MICRO REFINEMENTS ARE APPROVED FOR SPRINT 1 IMPLEMENTATION.

   - Device Management (Device Name, Type, Revocation)
   - Companion Presence (State Sync Data Payload)
   - Task Timeline Stream (Structured Progress JSON)
   - Notification Policy Mapping (EventBus Priorities)
   - Mobile Connection Resilience (Auto Reconnect UI)

   ZERO IMPACT ON FROZEN PLATFORMS.
######################################################################
```
