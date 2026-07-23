# CHITTI V2 — CAPABILITY ENHANCEMENT ANALYSIS
**(WAVE 1 — SPRINT 1: FEATURE: REMOTE_COMPANION)**

======================================================================
## 1. EXECUTIVE SUMMARY
======================================================================

Following the mandatory pre-implementation audit (`PRE_IMPLEMENTATION_AUDIT_REMOTE_COMPANION.md`), an enhancement analysis was performed to identify safe, high-value user experience, mobile UI, security, and recovery enhancements that naturally extend the existing canonical **`ChannelRuntime` (`desktop/runtimes/channel/`)**.

### Canonical Core Principles:
1. **`ChannelRuntime` is Canonical:** All mobile web chat interaction, WebSocket transport, device trust, and pairing operate strictly through `ChannelRuntime`.
2. **Zero Architecture Redesign:** No new networking frameworks or redundant communication runtimes will be created.
3. **Zero Impact on Frozen Platforms:** Character Platform, Desktop UI Runtime Foundation, Motion Design System, and Cognitive Core V1 remain 100% untouched.

---

======================================================================
## 2. FEATURE ENHANCEMENT EVALUATION MATRIX
======================================================================

| Feature / Capability | Status | Canonical Owner | Repository Location | Files to Extend | Implementation Priority |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **QR Pairing Payload** | **Already Exists** | `PairingService` | `desktop/runtimes/channel/pairing/service.py` | `service.py` | Core (Complete) |
| **6-Digit PIN Pairing** | **Missing** | `PairingService` | `desktop/runtimes/channel/pairing/service.py` | `service.py` | **Sprint 1 (High)** |
| **Trusted Devices Registry** | **Already Exists** | `PairingService` | `desktop/runtimes/channel/models/core.py` | `core.py` | Core (Complete) |
| **Device Rename / Alias** | **Nice To Have** | `PairingService` | `desktop/runtimes/channel/models/core.py` | `core.py` | **Sprint 1 (Medium)**|
| **Multiple Paired Devices** | **Already Exists** | `WebSocketTransport` | `desktop/runtimes/channel/transport/websocket.py` | `websocket.py` | Core (Complete) |
| **Session Resume & Token Auth**| **Already Exists** | `PairingService` | `desktop/runtimes/channel/pairing/service.py` | `service.py` | Core (Complete) |
| **Heartbeat & Offline Detect** | **Already Exists** | `WebSocketTransport` | `desktop/runtimes/channel/transport/websocket.py` | `websocket.py` | Core (Complete) |
| **Connection Auto-Reconnect** | **Missing** | Mobile Web UI | `frontend/remote_mobile/index.html` | `index.html` | **Sprint 1 (High)** |
| **Task Progress Stream** | **Missing** | `ChannelRouter` | `desktop/runtimes/channel/router/output.py` | `output.py` | **Sprint 1 (High)** |
| **Remote Task Toasts** | **Missing** | `ChannelRouter` | `desktop/runtimes/channel/router/output.py` | `output.py` | **Sprint 1 (Medium)**|
| **Voice ↔ Chat Sync** | **Already Exists** | `ChannelRouter` | `desktop/runtimes/channel/router/input.py` | `input.py` | Core (Complete) |
| **Desktop Screenshot Push** | **Missing** | `ChannelRuntime` | `desktop/runtimes/channel/channel_runtime.py` | `channel_runtime.py` | **Sprint 1 (High)** |
| **Chunked File Transfer** | **Already Exists** | `TransferManager` | `desktop/runtimes/channel/services/transfer_manager.py` | `transfer_manager.py`| Core (Complete) |
| **Mobile File Download** | **Missing** | Mobile Web UI | `frontend/remote_mobile/index.html` | `index.html` | **Sprint 1 (High)** |
| **Mobile File Upload** | **Missing** | Mobile Web UI | `frontend/remote_mobile/index.html` | `index.html` | **Sprint 1 (High)** |
| **Clipboard Sync (Remote)** | **Nice To Have** | `ChannelRuntime` | `desktop/runtimes/channel/channel_runtime.py` | `channel_runtime.py` | **Sprint 1 (Low)** |
| **Mobile Mascot Presence** | **Nice To Have** | Mobile Web UI | `frontend/remote_mobile/index.html` | `index.html` | **Sprint 1 (Medium)**|
| **Mobile Widget Dashboard** | **Nice To Have** | Mobile Web UI | `frontend/remote_mobile/index.html` | `index.html` | **Sprint 1 (Medium)**|
| **Dark / Light Theme** | **Nice To Have** | Mobile Web UI | `frontend/remote_mobile/index.html` | `index.html` | **Sprint 1 (Low)** |
| **Conversation History Sync** | **Already Exists** | `ChannelRouter` | `desktop/runtimes/channel/router/input.py` | `input.py` | Core (Complete) |
| **Typing Indicator** | **Nice To Have** | Mobile Web UI | `frontend/remote_mobile/index.html` | `index.html` | **Sprint 1 (Low)** |
| **Rate Limiting & Anti-Brute**| **Missing** | `PairingService` | `desktop/runtimes/channel/pairing/service.py` | `service.py` | **Sprint 1 (High)** |
| **Session Auto-Timeout** | **Already Exists** | `PairingService` | `desktop/runtimes/channel/pairing/service.py` | `service.py` | Core (Complete) |
| **LAN mDNS Discovery** | **Missing** | `ChannelRuntime` | `desktop/runtimes/channel/discovery/mdns.py` | `mdns.py` | **Sprint 1 (High)** |
| **LAN Static HTTP Host** | **Missing** | `ChannelRuntime` | `desktop/runtimes/channel/channel_runtime.py` | `channel_runtime.py` | **Sprint 1 (High)** |

---

======================================================================
## 3. RECOMMENDED ENHANCEMENTS FOR SPRINT 1
======================================================================

### 3.1 Mobile Web UI Experience (`frontend/remote_mobile/index.html`):
- **Single Page App (SPA):** Lightweight vanilla HTML5/CSS3/JS app requiring ZERO mobile app installation.
- **Mobile Chat Interface:** Responsive chat timeline synchronized live with desktop audio/text interaction.
- **Slime Mascot Avatar Badge:** Displays CHITTI's current visual state (`Speaking`, `Thinking`, `Working`, `Idle`) on mobile header.
- **Task Notifications & Progress Bar:** Real-time visual progress indicator during capability execution.
- **File Download & Upload Controls:** Direct mobile upload button and file download links bound to `TransferManager`.
- **Auto-Reconnect Socket:** Exponential backoff socket reconnection handler for seamless connection recovery when switching Wi-Fi networks.

### 3.2 Security & Device Trust Enhancements:
- **6-Digit PIN Pairing Fallback:** Allows manual PIN entry on mobile if camera QR scanning is unavailable.
- **Rate Limiting:** Maximum 5 failed PIN attempts per minute to prevent brute-force pairing attacks.
- **Local Network Discovery (mDNS):** Broadcasts `_chitti._tcp.local.` on port 9090 so phones automatically discover CHITTI on local Wi-Fi without typing IP addresses.

### 3.3 Remote Screen & Task Visibility:
- **Desktop Screenshot Request:** Tap "Screen View" on phone to request a fresh desktop screenshot snapshot (delegates to `DesktopSource`).

---

======================================================================
## 4. ARCHITECTURE SAFETY & FROZEN PLATFORM PROTECTION
======================================================================

- **Character Platform:** **ZERO IMPACT.** Mobile mascot badge is pure data state rendered on phone HTML canvas. Character Runtime PNG rendering remains untouched.
- **Desktop UI Runtime Foundation:** **ZERO IMPACT.** Frameless desktop windows and GPU composition are unchanged.
- **Widget Framework:** **ZERO IMPACT.** Desktop widgets consume session data; mobile web UI visualizes session payload over WebSocket.
- **Visual Coordinator Platform:** **ZERO IMPACT.** `VisualCoordinator` broadcasts state changes over EventBus; `ChannelRouter` forwards state payloads to mobile.

---

======================================================================
## 5. FINAL RECOMMENDATION FOR SPRINT 1
======================================================================

```
######################################################################
                RECOMMENDED ENHANCEMENT ACTION PLAN

   Extend ChannelRuntime (desktop/runtimes/channel/) with 4 additions:
   1. LAN HTTP Static File Server (hosts frontend/remote_mobile/).
   2. 6-Digit PIN Fallback & Rate Limiting in PairingService.
   3. mDNS Local Network Broadcast Helper (desktop/runtimes/channel/discovery/).
   4. Single-Page Mobile Web Chat UI (frontend/remote_mobile/index.html).

   ALL OTHER INFRASTRUCTURE ALREADY EXISTS AND WILL BE REUSED 100%.
######################################################################
```
