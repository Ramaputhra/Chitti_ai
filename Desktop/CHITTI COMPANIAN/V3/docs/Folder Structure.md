# CHITTI Repository Structure

```
CHITTI/
│
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
├── PROJECT_OVERVIEW.md
├── TECH_STACK.md
├── ENGINEERING_RULES.md
├── ROADMAP.md
├── SECURITY.md
│
├──────────────────────────────────────────────
│
├── docs/
│   │
│   ├── architecture/
│   │   ├── System_Architecture.md
│   │   ├── Desktop_Architecture.md
│   │   ├── Firmware_Architecture.md
│   │   ├── Hardware_Architecture.md
│   │   ├── AI_Architecture.md
│   │   ├── Memory_Architecture.md
│   │   ├── Emotion_Architecture.md
│   │   ├── Vision_Architecture.md
│   │   ├── Voice_Architecture.md
│   │   ├── Plugin_Architecture.md
│   │   ├── API_Architecture.md
│   │   └── Communication.md
│   │
│   ├── electronics/
│   │
│   ├── firmware/
│   │
│   ├── desktop/
│   │
│   ├── api/
│   │
│   ├── testing/
│   │
│   ├── manufacturing/
│   │
│   └── roadmap/
│
├──────────────────────────────────────────────
│
├── desktop/
│   │
│   ├── app/
│   │
│   ├── ui/
│   │   ├── avatar/
│   │   ├── widgets/
│   │   ├── settings/
│   │   ├── dialogs/
│   │   ├── notifications/
│   │   ├── themes/
│   │   └── assets/
│   │
│   ├── core/
│   │   ├── conversation/
│   │   ├── memory/
│   │   ├── emotion/
│   │   ├── scheduler/
│   │   ├── personality/
│   │   ├── context/
│   │   ├── intent/
│   │   ├── skills/
│   │   ├── planner/
│   │   ├── reasoning/
│   │   ├── state_machine/
│   │   └── events/
│   │
│   ├── ai/
│   │   ├── openai/
│   │   ├── gemini/
│   │   ├── claude/
│   │   ├── ollama/
│   │   ├── router/
│   │   ├── prompts/
│   │   └── providers/
│   │
│   ├── voice/
│   │   ├── wakeword/
│   │   ├── stt/
│   │   ├── tts/
│   │   ├── vad/
│   │   ├── audio/
│   │   └── pipeline/
│   │
│   ├── vision/
│   │   ├── camera/
│   │   ├── face/
│   │   ├── object/
│   │   ├── ocr/
│   │   ├── gesture/
│   │   └── tracking/
│   │
│   ├── hardware/
│   │   ├── api/
│   │   ├── serial/
│   │   ├── usb/
│   │   ├── ble/
│   │   ├── simulation/
│   │   └── drivers/
│   │
│   ├── plugins/
│   │
│   ├── sdk/
│   │
│   ├── database/
│   │
│   ├── storage/
│   │
│   ├── config/
│   │
│   └── utils/
│
├──────────────────────────────────────────────
│
├── firmware/
│   │
│   ├── esp32/
│   │   ├── app/
│   │   ├── hal/
│   │   ├── drivers/
│   │   │   ├── display/
│   │   │   ├── servo/
│   │   │   ├── audio/
│   │   │   ├── sensors/
│   │   │   ├── rtc/
│   │   │   ├── battery/
│   │   │   └── leds/
│   │   │
│   │   ├── communication/
│   │   ├── protocol/
│   │   ├── tasks/
│   │   ├── config/
│   │   ├── boot/
│   │   ├── ota/
│   │   └── tests/
│   │
│   └── simulator/
│
├──────────────────────────────────────────────
│
├── hardware/
│   │
│   ├── motherboard/
│   ├── sensor_board/
│   ├── power_board/
│   ├── body_board/
│   ├── display_board/
│   ├── accessories/
│   ├── cad/
│   ├── enclosure/
│   ├── gerbers/
│   ├── bom/
│   ├── datasheets/
│   └── manufacturing/
│
├──────────────────────────────────────────────
│
├── shared/
│   │
│   ├── protocol/
│   ├── constants/
│   ├── models/
│   ├── schemas/
│   ├── enums/
│   └── utilities/
│
├──────────────────────────────────────────────
│
├── cloud/
│   │
│   ├── api/
│   ├── sync/
│   ├── auth/
│   ├── ota/
│   ├── analytics/
│   └── notifications/
│
├──────────────────────────────────────────────
│
├── testing/
│   │
│   ├── unit/
│   ├── integration/
│   ├── hardware/
│   ├── ui/
│   ├── firmware/
│   ├── stress/
│   ├── performance/
│   └── regression/
│
├──────────────────────────────────────────────
│
├── scripts/
│
├── tools/
│
├── docker/
│
├── ci/
│
├── build/
│
├── releases/
│
├── assets/
│   ├── sounds/
│   ├── icons/
│   ├── fonts/
│   ├── avatars/
│   ├── animations/
│   └── videos/
│
└── experiments/
    ├── prototypes/
    ├── research/
    └── archive/
```

---

## Repository Layers

```
Level 1
---------
Documentation

Desktop

Firmware

Hardware

Shared

Cloud

Testing

Assets

Releases

---

Level 2
---------
Business Logic

AI

Memory

Emotion

Voice

Vision

Hardware API

Plugins

---

Level 3
---------
Implementation

Drivers

Protocols

Database

Utilities

Configuration

Tests

Assets
```

---

## Architectural Rule

Everything depends on the **Core**.

Nothing depends directly on Firmware.

Nothing depends directly on Electronics.

Hardware is replaceable.

Desktop is permanent.

AI Providers are replaceable.

Plugins are independent.

This keeps Chitti scalable for many years without major rewrites.