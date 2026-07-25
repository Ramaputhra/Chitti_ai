# Vizzu V2 — DESKTOP UI STUDIO GUIDE

## 1. Executive Summary
Desktop UI Studio (`desktop/ui/studio/`) is the single canonical repository for all lightweight UI assets, overlays, notifications, indicators, badges, timers, countdowns, dialogs, icons, animations, and system-state visual components across Vizzu V2.

---

## 2. Directory Structure Overview
```
desktop/ui/studio/
├── setup_ui_studio.py
├── assets/
│   ├── overlays/
│   ├── dialogs/
│   ├── notifications/
│   ├── countdown/
│   ├── timers/
│   ├── badges/
│   ├── indicators/
│   ├── icons/
│   ├── animations/
│   ├── sounds/
│   ├── widgets/
│   ├── transitions/
│   ├── themes/
│   └── mock/
└── documentation/
    ├── UI_STUDIO_GUIDE.md
    ├── PROCEED.md
    └── UI_STUDIO_FOUNDATION_REPORT.md
```

---

## 3. Platform Boundaries & Isolation
- **NO Character Assets:** Desktop UI Studio contains ZERO avatar models, character frame sequences, or voice profiles.
- **NO Presentation Assets:** Desktop UI Studio contains ZERO multi-renderer presentation bundles, executive dashboards, or complex experience studio templates.
- **System Interface Focus:** Desktop UI Studio owns lightweight desktop system overlays, toasts, status badges, timers, countdowns, and sound effects.

---

## 4. UI Event Mapping Matrix

| System Event | Desktop UI Studio Asset | Category | Description |
|---|---|---|---|
| `ReminderCreated` | `ReminderCreated.png` | `reminder` | Toast overlay confirming reminder creation |
| `EmailReceived` | `EmailReceived.png` | `email` | Corner notification for new email |
| `AlarmTriggered` | `AlarmRinging.png` | `alarm` | Ringing alarm dialog & countdown overlay |
| `ShutdownScheduled` | `ShutdownCountdown.png` | `shutdown` | System shutdown timer overlay |
| `PrintingStarted` | `Printing.png` | `printer` | Printer progress badge |
| `DownloadProgress` | `DownloadProgress.png` | `download` | Download progress ring overlay |
| `BatteryLow` | `BatteryLow.png` | `system_status` | Critical battery warning badge |
