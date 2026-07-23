# GRAPHIC DESIGNER HANDBOOK & ASSET REPLACEMENT GUIDE (PROCEED.md)

Welcome to the **CHITTI V2 Desktop UI Studio Asset Pipeline**. This guide provides exact instructions for graphic designers and UI engineers on how to replace placeholder PNG overlays, SVG icons, sounds, and CSS animations.

---

## 1. How to Replace PNG UI Assets
1. Export your UI overlay/badge artwork at 320x180 resolution with 8-bit alpha transparency (`RGBA`).
2. Overwrite the corresponding target file inside `desktop/ui/studio/assets/<category>/<item_name>.png`.

---

## 2. How to Replace SVG Icons
1. Export vector icon artwork at 200x200 resolution with viewBox `0 0 200 200`.
2. Save vector files to `desktop/ui/studio/assets/icons/<icon_name>.svg`.

---

## 3. How to Replace Sounds
1. Place short 16-bit 44.1kHz WAV sound effects inside `desktop/ui/studio/assets/sounds/`.
2. **STRICT RULE:** Speech/spoken audio is strictly forbidden in UI sound files.

---

## 4. How to Add New UI Assets & Animations
1. Create new PNG asset + JSON metadata file under the appropriate category folder in `assets/`.
2. Add corresponding CSS animation keyframes to `assets/animations/<animation_name>/`.

---

## 5. Naming Conventions & Permanent Asset IDs
- Asset IDs use the format `UI_<CATEGORY>_<ITEM_NAME>` (e.g., `UI_ALARM_ALARMSET`, `UI_REMINDER_REMINDERCREATED`).

---

## 6. Recommended PNG Resolution & Transparency Rules
- Resolution: **320x180** or **200x200** square for badges.
- Background: Must use transparent RGBA background layers.

---

## 7. Packaging & Validation Checklist
- [ ] RGBA PNG file present at expected resolution.
- [ ] Associated JSON metadata present.
- [ ] SVG icons formatted cleanly.
- [ ] Sound WAV files contain non-speech sound effects.
