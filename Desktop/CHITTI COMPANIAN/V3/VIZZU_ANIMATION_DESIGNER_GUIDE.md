# VIZZU AI Companion - Animation Design Guide
## Complete Specification for Graphic Designer

---

## 📋 TABLE OF CONTENTS
1. [Project Overview](#project-overview)
2. [Technical Specifications](#technical-specifications)
3. [Animation Categories](#animation-categories)
4. [Complete Animation List](#complete-animation-list)
5. [Voice Command Flow Examples](#voice-command-flow-examples)
6. [Frame-by-Frame Templates](#frame-by-frame-templates)
7. [Sound Effects List](#sound-effects-list)
8. [Deliverables Checklist](#deliverables-checklist)

---

## 🎯 PROJECT OVERVIEW

**Project:** VIZZU AI Desktop Companion  
**Type:** Windows Desktop AI Assistant with Voice Control  
**Avatar:** Cute robot companion character  
**Style:** Friendly, approachable, expressive

### Core Capabilities
- **Desktop Automation:** File operations, folder management, system settings
- **Browser Automation:** Web browsing, form filling, search
- **Calendar/Reminders:** Set timers, reminders, calendar events
- **Memory:** Remember user preferences, past interactions
- **Presentation:** Open folders, show results, notifications

---

## 🔧 TECHNICAL SPECIFICATIONS

### Animation Requirements
| Property | Value |
|----------|-------|
| **Format** | PNG sequences |
| **Frame Rate** | 14 FPS |
| **Frames per Animation** | 14 frames (1 second) |
| **Extended Animations** | 21 frames (1.5 seconds) |
| **Looping Animations** | 7 frames seamless loop |
| **Resolution** | 512x512px (scalable) |
| **Background** | Transparent (PNG with alpha) |

### File Naming Convention
```
{AnimationName}_{FrameNumber:003}.png
Example: WakeDetected_001.png, WakeDetected_002.png, ... WakeDetected_014.png
```

### Folder Structure
```
assets/avatar/
├── expressions/
│   ├── SYSTEM/
│   │   ├── BootStart/
│   │   ├── BootProgress/
│   │   ├── BootComplete/
│   │   ├── IdleToDot/
│   │   ├── DotIdle/
│   │   ├── IntroDot1/
│   │   ├── IntroDot2/
│   │   ├── IntroDot3/
│   │   ├── Stretch1Min/
│   │   ├── Stretch2Min/
│   │   ├── Goodbye/
│   │   └── Shutdown/
│   ├── SPEECH/
│   │   ├── WakeDetected/
│   │   ├── ListeningActive/
│   │   ├── ListeningPulse/
│   │   ├── ProcessingCommand/
│   │   └── Understanding/
│   ├── EXECUTION/
│   │   ├── ExecutingGeneral/
│   │   ├── ExecutingFile/
│   │   ├── ExecutingBrowser/
│   │   ├── ExecutingApp/
│   │   ├── ExecutingCalendar/
│   │   ├── ExecutingClipboard/
│   │   ├── ExecutingSearch/
│   │   └── ExecutingSystem/
│   ├── RESULT/
│   │   ├── TaskSuccess/
│   │   ├── TaskPartial/
│   │   ├── TaskFailed/
│   │   ├── TaskBlocked/
│   │   ├── WaitingConfirm/
│   │   └── Confirming/
│   ├── TALKING/
│   │   ├── Talking/
│   │   ├── TalkingShort/
│   │   └── TalkingExplain/
│   └── IDLE/
│       ├── IdleNormal/
│       ├── IdleHappy/
│       ├── IdleCurious/
│       ├── IdleWaiting/
│       └── IdleBlink/
└── sounds/
    ├── boot_start.wav
    ├── ready.wav
    ├── wake_beep.wav
    ├── wake_pop.wav
    ├── wake_slide.wav
    ├── wake_fade.wav
    ├── success_chime.wav
    ├── error_tone.wav
    ├── bye.wav
    └── notification.wav
```

---

## 📁 ANIMATION CATEGORIES

### 1. SYSTEM ANIMATIONS (13 total)
*Lifecycle animations - boot, minimize, wake*

| # | Animation | Duration | Loop | Description |
|---|----------|---------|------|-------------|
| 1 | `BootStart` | 1.5s | No | Eyes opening sequence |
| 2 | `BootProgress` | 2s+ | Yes | Loading spinner/progress |
| 3 | `BootComplete` | 1s | No | Ready to interact |
| 4 | `IdleToDot` | 2s | No | Shrinking to system tray |
| 5 | `DotIdle` | ∞ | Yes | Minimal pulsing dot |
| 6 | `IntroDot1` | 1.5s | No | **Pop expand** from dot |
| 7 | `IntroDot2` | 1.5s | No | **Slide in** from dot |
| 8 | `IntroDot3` | 1.5s | No | **Fade grow** from dot |
| 9 | `Stretch1Min` | 0.5s | No | Quick stretch at 1min idle |
| 10 | `Stretch2Min` | 0.8s | No | Full stretch at 2min idle |
| 11 | `Goodbye` | 2s | No | Wave and fade out |
| 12 | `Shutdown` | 1.5s | No | Eyes close, final pose |

### 2. SPEECH ANIMATIONS (5 total)
*Voice recognition and listening*

| # | Animation | Duration | Loop | Description |
|---|----------|---------|------|-------------|
| 13 | `WakeDetected` | 0.5s | No | Eyes light up on wake word |
| 14 | `ListeningActive` | 1s+ | Yes | Attentive listening pose |
| 15 | `ListeningPulse` | 0.3s | Yes | Pulse with speech |
| 16 | `ProcessingCommand` | 0.8s | No | Thinking nod gesture |
| 17 | `Understanding` | 0.5s | No | Recognition confirmed |

### 3. EXECUTION ANIMATIONS (8 total)
*Task performing animations*

| # | Animation | Duration | Loop | Description |
|---|----------|---------|------|-------------|
| 18 | `ExecutingGeneral` | 1s+ | Yes | Generic task working |
| 19 | `ExecutingFile` | 1s+ | Yes | File/folder operations |
| 20 | `ExecutingBrowser` | 1s+ | Yes | Browser automation |
| 21 | `ExecutingApp` | 1s+ | Yes | App launch/control |
| 22 | `ExecutingCalendar` | 1s+ | Yes | Timer/reminder/calendar |
| 23 | `ExecutingClipboard` | 0.5s+ | Yes | Copy/paste operations |
| 24 | `ExecutingSearch` | 1s+ | Yes | Search operations |
| 25 | `ExecutingSystem` | 1s+ | Yes | System settings |

### 4. RESULT ANIMATIONS (6 total)
*Success/failure responses*

| # | Animation | Duration | Loop | Description |
|---|----------|---------|------|-------------|
| 26 | `TaskSuccess` | 1.5s | No | Happy success - happy nod |
| 27 | `TaskPartial` | 1.2s | No | Partial success - satisfied |
| 28 | `TaskFailed` | 1.5s | No | Task failed - concerned |
| 29 | `TaskBlocked` | 1s | No | Blocked - problem indication |
| 30 | `WaitingConfirm` | 1s+ | Yes | Waiting for user input |
| 31 | `Confirming` | 0.8s | No | Asking for confirmation |

### 5. TALKING ANIMATIONS (3 total)
*Speaking responses*

| # | Animation | Duration | Loop | Description |
|---|----------|---------|------|-------------|
| 32 | `Talking` | 1s+ | Yes | Normal speaking |
| 33 | `TalkingShort` | 0.5s+ | Yes | Brief response |
| 34 | `TalkingExplain` | 1.5s+ | Yes | Detailed explanation |

### 6. IDLE ANIMATIONS (5 total)
*Ambient waiting states*

| # | Animation | Duration | Loop | Description |
|---|----------|---------|------|-------------|
| 35 | `IdleNormal` | ∞ | Yes | Default calm idle |
| 36 | `IdleHappy` | ∞ | Yes | Happy content idle |
| 37 | `IdleCurious` | ∞ | Yes | Alert curious idle |
| 38 | `IdleWaiting` | ∞ | Yes | Patient waiting idle |
| 39 | `IdleBlink` | 0.2s | Yes | Blink cycle overlay |

---

## 🔄 VOICE COMMAND FLOW EXAMPLES

### Example 1: "Set reminder for after 15 minutes"
```
User: "Hey Vizzu, set a reminder for 15 minutes"

Flow Timeline:
──────────────────────────────────────────────────────────────
 0.0s  │ WAKE_WORD detected
       │ → BootStart (0.5s)
       │
 0.5s  │ LISTENING state
       │ → ListeningActive (loop)
       │
 2.0s  │ User stops speaking, SILENCE detected
       │ → Understanding (0.5s)
       │
 2.5s  │ INTENT_PARSED
       │ → ProcessingCommand (0.8s)
       │
 3.3s  │ EXECUTING task (set_reminder)
       │ → ExecutingCalendar (1s+ loop)
       │
 4.5s  │ TASK_COMPLETED
       │ → TaskSuccess (1.5s)
       │
 6.0s  │ Speaking: "Done! Reminder set for 15 minutes"
       │ → TalkingExplain (loop while speaking)
       │
 8.0s  │ Response complete
       │ → IdleNormal (loop)
       │
 60s   │ IDLE_1MIN
       │ → Stretch1Min (0.5s)
       │
 120s  │ IDLE_2MIN
       │ → IdleToDot (2s) → DotIdle
──────────────────────────────────────────────────────────────
```

### Example 2: "Open Downloads folder"
```
User: "Hey Vizzu, open Downloads"

Flow Timeline:
──────────────────────────────────────────────────────────────
 0.0s  │ WakeDetected (0.5s)
 0.5s  │ ListeningActive
 1.5s  │ Understanding (0.5s)
 2.0s  │ ExecutingFile (0.8s)
 2.8s  │ TaskSuccess (1.5s)
 4.3s  │ TalkingShort (while speaking)
 5.5s  │ IdleNormal
──────────────────────────────────────────────────────────────
```

### Example 3: "Thanks, bye!"
```
User: "Thanks, bye!"

Flow Timeline:
──────────────────────────────────────────────────────────────
 0.0s  │ WakeDetected (0.5s)
 0.5s  │ ListeningActive
 1.5s  │ Understanding (0.5s)
 2.0s  │ GOODBYE intent detected
       │ → Goodbye (2s) - Wave animation
 4.0s  │ → IdleToDot (2s)
 6.0s  │ → DotIdle (loop until wake)
──────────────────────────────────────────────────────────────
```

### Example 4: Wake from System Tray (3 variants)
```
User clicks on dot OR says wake word

VARIANT 1 - Pop Expand:
──────────────────────────────────────────────────────────────
 0.0s  │ Dot pops to full size with scale bounce
 0.5s  │ Eyes appear with light up effect
 1.0s  │ Settle into Ready pose
 1.5s  │ → ListeningActive
──────────────────────────────────────────────────────────────

VARIANT 2 - Slide In:
──────────────────────────────────────────────────────────────
 0.0s  │ Dot slides up/expands horizontally
 0.5s  │ Eyes fade in
 1.0s  │ Full character visible
 1.5s  │ → ListeningActive
──────────────────────────────────────────────────────────────

VARIANT 3 - Fade Grow:
──────────────────────────────────────────────────────────────
 0.0s  │ Dot fades while growing
 0.5s  │ Character silhouette appears
 1.0s  │ Full opacity, details fill in
 1.5s  │ → ListeningActive
──────────────────────────────────────────────────────────────
```

---

## 🎨 FRAME-BY-FRAME TEMPLATES

### Standard Animation (14 frames)
```
Frame 1-3:   Start/Rest position (neutral)
Frame 4-7:    Build up to expression
Frame 8-10:   Peak expression/emotion
Frame 11-14:  Return to neutral OR hold
```

### Looping Animation (7 frames)
```
Frame 1-7:    Complete loop
(Frames 1-7 repeat seamlessly)
```

### Stretch Animation (7 frames)
```
Frame 1-2:    Neutral idle pose
Frame 3-4:    Begin stretch motion
Frame 5:      Peak stretch
Frame 6-7:    Return to idle
```

### Goodbye Animation (21 frames)
```
Frame 1-5:    Normal → Wave start
Frame 6-12:   Wave motion
Frame 13-16:  Wave complete → Begin fade
Frame 17-21:  Fade out / shrink
```

### Idle-to-Dot Animation (21 frames)
```
Frame 1-5:    Idle → Begin shrink
Frame 6-14:   Shrinking down
Frame 15-18:  Become small dot
Frame 19-21:  Dot pulse/final pose
```

---

## 🔊 SOUND EFFECTS LIST

| # | Sound File | Trigger | Duration | Type |
|---|------------|---------|----------|------|
| 1 | `boot_start.wav` | App launch | ~1s | Electronic startup |
| 2 | `ready.wav` | Boot complete | ~0.5s | Confirmation beep |
| 3 | `wake_beep.wav` | Wake word detected | ~0.3s | Attention chime |
| 4 | `wake_pop.wav` | Intro variant 1 | ~0.5s | Pop/bounce SFX |
| 5 | `wake_slide.wav` | Intro variant 2 | ~0.5s | Slide SFX |
| 6 | `wake_fade.wav` | Intro variant 3 | ~0.5s | Fade-in whoosh |
| 7 | `success_chime.wav` | Task success | ~1s | Happy chime |
| 8 | `error_tone.wav` | Task failed | ~0.5s | Error buzzer |
| 9 | `bye.wav` | Goodbye animation | ~0.5s | Farewell tone |
| 10 | `notification.wav` | New info | ~0.3s | Notification ping |

---

## ✅ DELIVERABLES CHECKLIST

### SYSTEM Animations (12)
- [ ] BootStart (14 frames)
- [ ] BootProgress (14 frames, loop)
- [ ] BootComplete (14 frames)
- [ ] IdleToDot (21 frames)
- [ ] DotIdle (7 frames, loop)
- [ ] IntroDot1 (14 frames)
- [ ] IntroDot2 (14 frames)
- [ ] IntroDot3 (14 frames)
- [ ] Stretch1Min (7 frames)
- [ ] Stretch2Min (7 frames)
- [ ] Goodbye (21 frames)
- [ ] Shutdown (14 frames)

### SPEECH Animations (5)
- [ ] WakeDetected (7 frames)
- [ ] ListeningActive (14 frames, loop)
- [ ] ListeningPulse (7 frames, loop)
- [ ] ProcessingCommand (14 frames)
- [ ] Understanding (7 frames)

### EXECUTION Animations (8)
- [ ] ExecutingGeneral (14 frames, loop)
- [ ] ExecutingFile (14 frames, loop)
- [ ] ExecutingBrowser (14 frames, loop)
- [ ] ExecutingApp (14 frames, loop)
- [ ] ExecutingCalendar (14 frames, loop)
- [ ] ExecutingClipboard (7 frames, loop)
- [ ] ExecutingSearch (14 frames, loop)
- [ ] ExecutingSystem (14 frames, loop)

### RESULT Animations (6)
- [ ] TaskSuccess (14 frames)
- [ ] TaskPartial (14 frames)
- [ ] TaskFailed (14 frames)
- [ ] TaskBlocked (14 frames)
- [ ] WaitingConfirm (14 frames, loop)
- [ ] Confirming (14 frames)

### TALKING Animations (3)
- [ ] Talking (14 frames, loop)
- [ ] TalkingShort (7 frames, loop)
- [ ] TalkingExplain (21 frames, loop)

### IDLE Animations (5)
- [ ] IdleNormal (7 frames, loop)
- [ ] IdleHappy (7 frames, loop)
- [ ] IdleCurious (7 frames, loop)
- [ ] IdleWaiting (7 frames, loop)
- [ ] IdleBlink (3 frames, loop)

### SOUND EFFECTS (10)
- [ ] boot_start.wav
- [ ] ready.wav
- [ ] wake_beep.wav
- [ ] wake_pop.wav
- [ ] wake_slide.wav
- [ ] wake_fade.wav
- [ ] success_chime.wav
- [ ] error_tone.wav
- [ ] bye.wav
- [ ] notification.wav

---

## 📊 SUMMARY STATISTICS

| Category | Count | Total Frames | Looping |
|---------|-------|--------------|---------|
| System | 12 | ~200 | 1 |
| Speech | 5 | ~60 | 2 |
| Execution | 8 | ~110 | 8 |
| Result | 6 | ~90 | 1 |
| Talking | 3 | ~50 | 3 |
| Idle | 5 | ~30 | 5 |
| **TOTAL** | **39** | **~540** | **20** |

### Sound Effects: 10 files

---

## 🎨 DESIGN NOTES

### Character Style Guidelines
- **Type:** Cute, friendly robot companion
- **Eyes:** Large, expressive - main communication channel
- **Body:** Simple geometric shapes
- **Colors:** Soft blue (#4A90D9) primary, teal accents
- **Style:** Modern, clean, approachable

### Expression Guidelines
- Start and end frames should be neutral/rest positions
- Peak emotion should occur at frames 8-10 for standard animations
- Smooth transitions between expressions
- Eyes are the primary focus for expressions

### Animation Guidelines
- Keep movements subtle and friendly
- Avoid jarring or aggressive motions
- Use easing for smooth motion (ease-in-out)
- Looping animations must be seamless

---

*Created for VIZZU AI Companion - 2026*
*Source files: `desktop/runtimes/expression/expressions.json`, `desktop/platform/core/animation_orchestrator.py`*
