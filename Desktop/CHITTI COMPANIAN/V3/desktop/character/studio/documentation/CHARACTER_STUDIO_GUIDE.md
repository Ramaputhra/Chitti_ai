# CHITTI V2 — CHARACTER STUDIO GUIDE

## 1. Executive Summary
Character Studio (`desktop/character/studio/`) serves as the single canonical repository for all character source vector assets, 2D PNG frame sequences, behavior metadata, props, sounds, and documentation in CHITTI V2.

---

## 2. Directory Structure Overview
```
desktop/character/studio/
├── assets/
│   ├── source/
│   │   └── character/
│   │       ├── body/
│   │       ├── head/
│   │       ├── face/ (eyes, eyebrows, nose, ears, cheeks, mouths, hair)
│   │       ├── hands/ (left, right)
│   │       ├── accessories/ (glasses, hat, headset)
│   │       └── props/ (laptop, notebook, magnifier, etc.)
│   └── runtime/
│       ├── behaviors/ (system, listening, thinking, speaking, working, gestures, vision, navigation, reminders, success, warning, transitions)
│       ├── props/
│       ├── sounds/
│       ├── metadata/
│       └── placeholders/
└── documentation/
    ├── CHARACTER_STUDIO_GUIDE.md
    ├── BEHAVIOR_CATALOG.md
    ├── PROCEED.md
    └── CHARACTER_STUDIO_MIGRATION_AUDIT.md
```

---

## 3. Behavior Clip Architecture
Every behavior clip folder contains:
- `Frame01.png` .. `Frame14.png`: 14-frame animation sequence at 14 FPS.
- `behavior.json`: Structured metadata containing permanent `CHR_` behavior ID, FPS, duration, loop flag, priority, blend mode, and sound file link.
- `sound.wav`: Placeholder sound effect file (Speech is strictly forbidden in sound files).

---

## 4. Naming Conventions & Permanent Behavior IDs
All behaviors are assigned permanent IDs starting with `CHR_`:
- System: `CHR_BOOT_001`, `CHR_WAKE_001`, `CHR_IDLE_001`
- Listening: `CHR_LISTEN_001`
- Thinking: `CHR_THINK_001`
- Speaking: `CHR_TALK_NEUTRAL_001`, `CHR_TALK_HAPPY_001`
- Working: `CHR_WORK_TYPING_001`, `CHR_WORK_CODING_001`
- Gestures: `CHR_GEST_POINT_L_001`, `CHR_GEST_PRES_DASH_001`
- Success: `CHR_SUCC_THUMBSUP_001`, `CHR_SUCC_CELEBRATE_001`
- Warning: `CHR_WARN_001`, `CHR_WARN_ERR_001`

*Note: Expression Engine references permanent `behavior_id` strings, NEVER raw filenames.*
