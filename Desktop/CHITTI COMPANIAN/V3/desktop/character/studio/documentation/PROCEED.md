# GRAPHIC DESIGNER HANDBOOK & ASSET REPLACEMENT GUIDE (PROCEED.md)

Welcome to the **CHITTI V2 Character Studio Asset Pipeline**. This guide provides exact instructions for graphic designers and animators on how to replace placeholder assets, add new behavior clips, and maintain production quality across the platform.

---

## Section 1: Repository Overview
All character assets reside exclusively inside `desktop/character/studio/`. This repository is divided into `assets/source/` (vector SVG source files) and `assets/runtime/` (production 2D PNG frame sequences, behavior metadata, props, and sound effects).

---

## Section 2: Folder Hierarchy
```
desktop/character/studio/assets/
├── source/
│   └── character/
│       ├── body/
│       ├── head/
│       ├── face/ (eyes, eyebrows, nose, ears, cheeks, mouths, hair)
│       ├── hands/ (left, right)
│       ├── accessories/ (glasses, hat, headset)
│       └── props/ (laptop, notebook, coffee, etc.)
└── runtime/
    ├── behaviors/ (system, listening, thinking, speaking, working, gestures, vision, navigation, reminders, success, warning, transitions)
    ├── props/
    ├── sounds/
    ├── metadata/
    └── placeholders/
```

---

## Section 3: Behavior Naming Rules
- Use lower_snake_case for behavior folder names (e.g., `typing_laptop`, `idle_blink`, `talking_neutral`).
- Folders must be placed in their appropriate category directory under `assets/runtime/behaviors/`.

---

## Section 4: Behavior ID Rules
- Every behavior MUST be assigned a permanent ID starting with `CHR_` (e.g., `CHR_IDLE_001`, `CHR_WORK_TYPING_001`).
- Permanent IDs are declared in `behavior.json` and referenced by code. NEVER rename an ID once published.

---

## Section 5: Frame Naming Convention
- Every 2D frame sequence MUST follow 2-digit 1-indexed naming:
  - `Frame01.png`
  - `Frame02.png`
  ...
  - `Frame14.png`

---

## Section 6: How to Replace Placeholder PNG Sequences
1. Export your 14-frame animation from Adobe Animate, After Effects, Photoshop, or Blender.
2. Ensure frames are named `Frame01.png` through `Frame14.png`.
3. Overwrite the placeholder images inside the target behavior directory (e.g., `assets/runtime/behaviors/working/typing_laptop/`).

---

## Section 7: How to Replace Source SVG Assets
1. Open the target SVG in Adobe Illustrator, Inkscape, or Figma.
2. Edit or re-draw the vector artwork maintaining original viewBox scales (`400x400`).
3. Save as SVG in `assets/source/character/` under the appropriate category (`body`, `head`, `face`, `hands`, `accessories`, `props`).

---

## Section 8: How to Create New Behavior Clips
1. Create a new directory under `assets/runtime/behaviors/<category>/<new_behavior_name>/`.
2. Add `Frame01.png` .. `Frame14.png`.
3. Add `sound.wav` placeholder audio effect.
4. Copy `behavior.json` template, assign a unique `CHR_` behavior ID, and set `fps`, `duration`, and `loop` flags.

---

## Section 9: How to Update Existing Behavior Clips
1. Replace the frame images (`Frame01.png` .. `Frame14.png`).
2. If frame count or timing changes, update `total_frames` and `duration_seconds` in `behavior.json`.

---

## Section 10: How to Replace Props
1. Export a 300x300 transparent PNG preview to `assets/runtime/props/<prop_name>/prop_preview.png`.
2. Export vector source artwork to `assets/source/character/props/<prop_name>.svg`.

---

## Section 11: How to Replace Placeholder sound.wav
1. Place a short (0.3s - 1.5s) 16-bit 44.1kHz WAV sound effect inside the behavior directory as `sound.wav`.
2. **STRICT RULE:** Speech/voice lines are strictly forbidden in `sound.wav` (Speech belongs exclusively to TTS).

---

## Section 12: Recommended PNG Resolution
- Canvas Resolution: **512x512** pixels (or 300x300 minimum).
- Aspect Ratio: **1:1 square**.

---

## Section 13: Recommended Transparent Background Rules
- All PNG frames MUST have 8-bit alpha transparency (`RGBA`).
- Do not export with solid background layers or white margins.

---

## Section 14: Recommended Animation Timing
- Canonical Frame Rate: **14 FPS**.
- Total Duration: **1.0 second** (14 frames) for standard clips; 2.0 seconds (28 frames) for slow idles.

---

## Section 15: Looping Behavior Guidelines
- Set `"loop": true` in `behavior.json` for continuous states (`Idle`, `Listening`, `Thinking`, `TalkingNeutral`, `TypingLaptop`).
- Frame14 MUST seamlessly blend back into Frame01.

---

## Section 16: Transition Behavior Guidelines
- Transition clips (`IdleToTalk`, `SleepToWake`, etc.) must have `"loop": false`.
- Used by Expression Engine to smoothly blend between primary states.

---

## Section 17: Metadata Editing (behavior.json)
Ensure JSON keys are present and valid:
```json
{
  "behavior_id": "CHR_WORK_TYPING_001",
  "behavior_name": "TypingLaptop",
  "category": "working",
  "fps": 14,
  "total_frames": 14,
  "duration_seconds": 1.0,
  "loop": true,
  "priority": "NORMAL",
  "interruptible": true,
  "sound_file": "sound.wav"
}
```

---

## Section 18: Packaging Guidelines
When delivering asset packs, zip the target behavior folders keeping the exact relative paths under `assets/runtime/behaviors/`.

---

## Section 19: Asset Validation Checklist
- [ ] 14 PNG frames present (`Frame01.png` .. `Frame14.png`).
- [ ] Transparent RGBA background.
- [ ] `behavior.json` present with valid `CHR_` ID.
- [ ] `sound.wav` present (no spoken words).
- [ ] Seamless loop for continuous states.

---

## Section 20: Common Mistakes to Avoid
1. Forgetting transparent background (exporting black or white box).
2. Mismatch in frame numbers (`frame1.png` instead of `Frame01.png`).
3. Embedding spoken voice in sound files.
4. Changing permanent `behavior_id` strings after publication.

---

## Section 21: Graphic Designer Best Practices
- Keep character lines clean and vector-aligned.
- Use primary brand accent color `#6366f1` for highlights.
- Maintain consistent character scale across all behavior frames.

---

## Section 22: Engineering Integration Notes
`CharacterRuntime` indexes behaviors using `behavior.json` files. `ExpressionEngine` dispatches behaviors by permanent `behavior_id`.

---

## Section 23: Future Character Runtime Integration Overview
In future sprints, `CharacterRuntime` will load PNG sequences into texture atlases and play audio effects synchronously with TTS speech events via EventBus notifications.
