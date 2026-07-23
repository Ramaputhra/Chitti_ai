# CHITTI V2 — PERSONALITY SETTINGS GUI GUIDE

Welcome to the **CHITTI V2 Personality Settings GUI Guide**. This document describes the recommended UI layout for personality controls, trait sliders, presets, live preview, and import/export operations.

---

## 1. Recommended GUI Layout

```
+-----------------------------------------------------------------------+
| PERSONALITY SETTINGS STUDIO                                           |
+-----------------------------------------------------------------------+
| PRESETS: [ Friendly v ] [ Save Custom ] [ Import JSON ] [ Export JSON]|
+-----------------------------------------------------------------------+
| TRAIT SLIDERS                                                         |
| Professional : [=======---] 0.70                                     |
| Friendly     : [=========] 0.90                                     |
| Humorous     : [====------] 0.40                                     |
| Empathetic   : [========--] 0.80                                     |
| Motivational : [=======---] 0.70                                     |
| Concise      : [=====-----] 0.50                                     |
| Talkative    : [======----] 0.60                                     |
| Expressive   : [=======---] 0.70                                     |
+-----------------------------------------------------------------------+
| LIVE PREVIEW                                                          |
| Intent: OPEN_BROWSER                                                  |
| Output Text : "Right on it boss, opening your browser."               |
| Voice Rate  : 1.05x | Pause: 1.0x | Intonation: 1.1x                  |
| Behavior    : [CHR_GREET_MORNING_001] GreetingMorning                 |
| UI Badge    : "Browser ready, boss!"                                  |
+-----------------------------------------------------------------------+
```

---

## 2. GUI Sections
1. **Personality Sliders:** Interactive range sliders (0.0 to 1.0) with real-time value displays.
2. **Voice & Speech Adaptation:** Displays mapped voice parameters (`speech_rate`, `pause_length`, `emphasis`, `intonation_level`, `expression_level`, `voice_energy`).
3. **Live Preview Panel:** Displays sample LLM rewrite, behavior selection, and UI wording in real time.
4. **Preset Selector & Actions:** Dropdown to apply presets (Professional, Friendly, Teacher, Minimal, Motivational, Developer, Productivity Coach, Story Teller, Assistant) + Import/Export buttons.
