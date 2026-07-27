# VIZZU Animation State Machine - Complete Specification

## Overview
This document defines the complete animation/expression system for VIZZU AI Companion based on the voice command flow: **Listening → Performing Task → Success → Idle**

---

## 🎬 COMPLETE ANIMATION LIST BY CATEGORY

### 1. SYSTEM ANIMATIONS (Lifecycle)

| Animation | Trigger | Duration | Loop | Description |
|-----------|---------|----------|------|-------------|
| `boot_start` | App launch | 1.5s | No | Initial boot sequence - eyes opening |
| `boot_progress` | During boot | 2s | No | Loading animations - progress indicator |
| `boot_complete` | Boot finished | 1s | No | Ready state - eyes fully open |
| `idle_to_dot` | 2min idle | 2s | No | Shrinking to system tray dot |
| `dot_idle` | In system tray | ∞ | Yes | Minimal pulsing dot animation |
| `intro_from_dot_1` | Wake from dot | 1.5s | No | **Variant 1** - Pop expand |
| `intro_from_dot_2` | Wake from dot | 1.5s | No | **Variant 2** - Slide in |
| `intro_from_dot_3` | Wake from dot | 1.5s | No | **Variant 3** - Fade grow |
| `stretch_1min` | 1min idle | 0.5s | No | Quick stretch |
| `stretch_2min` | 2min idle | 0.8s | No | Full stretch before dot |
| `goodbye` | User says bye | 2s | No | Wave and fade out |
| `shutdown` | App close | 1.5s | No | Final animation before exit |

### 2. SPEECH/LISTENING ANIMATIONS

| Animation | Trigger | Duration | Loop | Description |
|-----------|---------|----------|------|-------------|
| `wake_detected` | Wake word heard | 0.5s | No | Eyes light up - attention |
| `listening_active` | After wake | 1s+ | Yes | Active listening - ear indicator |
| `listening_pulse` | User speaking | 0.3s | Yes | Pulse on speech detection |
| `processing_command` | Command understood | 0.8s | No | Thinking nod |
| `understanding` | Intent parsed | 0.5s | No | Recognition confirmed |

### 3. TASK EXECUTION ANIMATIONS

These map to **Desktop Automation Capabilities**:

| Animation | Trigger | Duration | Loop |
|-----------|---------|----------|------|
| `executing_general` | Generic task | 1s+ | Yes |
| `executing_file` | File operations | 1s+ | Yes |
| `executing_browser` | Browser tasks | 1s+ | Yes |
| `executing_app` | App launching | 1s+ | Yes |
| `executing_calendar` | Calendar/Reminder | 1s+ | Yes |
| `executing_clipboard` | Clipboard ops | 0.5s+ | Yes |
| `executing_search` | Search operations | 1s+ | Yes |
| `executing_system` | System settings | 1s+ | Yes |

### 4. RESULT/SUCCESS ANIMATIONS

| Animation | Trigger | Duration | Loop | Description |
|-----------|---------|----------|------|-------------|
| `task_success` | Task completed | 1.5s | No | Happy success - nod |
| `task_partial` | Partial success | 1.2s | No | Satisfied but not excited |
| `task_failed` | Task failed | 1.5s | No | Concerned expression |
| `task_blocked` | Blocked/Error | 1s | No | Problem indication |
| `waiting_for_confirm` | Needs input | 1s+ | Yes | Uncertain but waiting |
| `confirming` | Asking user | 0.8s | No | Question gesture |

### 5. IDLE ANIMATIONS (Ambient)

| Animation | Trigger | Duration | Loop | Description |
|-----------|---------|----------|------|-------------|
| `idle_normal` | Default idle | ∞ | Yes | Calm neutral |
| `idle_happy` | Positive mood | ∞ | Yes | Slight smile |
| `idle_curious` | After learning | ∞ | Yes | Slightly interested |
| `idle_waiting` | Expecting reply | ∞ | Yes | Patient waiting |
| `idle_blink` | Periodic | 0.2s | Yes | Normal blink cycle |

---

## 🔄 COMPLETE VOICE FLOW EXAMPLES

### Example 1: "Set reminder for after 15 min"
```
User: "Hey Vizzu, set a reminder for 15 minutes"
     ↓
[SpeechState: WAKE_DETECTED] → wake_detected (0.5s)
     ↓
[SpeechState: LISTENING] → listening_active (loop)
     ↓
[SpeechState: UNDERSTANDING] → understanding (0.5s)
     ↓
[Task: SET_REMINDER] → executing_calendar (1s+)
     ↓
[Result: SUCCESS] → task_success (1.5s)
     ↓
[Talking: "Done! Reminder set for 15 minutes"] → talking_explain (while speaking)
     ↓
[SpeechState: EXPECTING_REPLY] → idle_waiting (5s timeout)
     ↓
[SpeechState: IDLE] → idle_normal (loop)
     ↓
[2min idle] → stretch_1min (0.5s)
     ↓
[Continue idle] → idle_normal
     ↓
[2min more] → idle_to_dot (2s) → dot_idle
```

### Example 2: "Open Downloads folder"
```
User: "Hey Vizzu, open Downloads"
     ↓
wake_detected → listening_active → understanding
     ↓
[Task: FOLDER_OPEN] → executing_file (0.8s)
     ↓
task_success → talking_short → idle
```

### Example 3: "What time is it?"
```
User: "Hey Vizzu, what time is it?"
     ↓
wake_detected → listening_active → understanding
     ↓
[Task: TIME_QUERY] → idle_waiting (thinking pose)
     ↓
[Talking: "It's 2:30 PM"] → talking (while speaking)
     ↓
idle_normal
```

### Example 4: "Thanks, bye!"
```
User: "Thanks, bye!"
     ↓
wake_detected → listening_active → understanding
     ↓
[Task: GOODBYE] → goodbye (2s)
     ↓
idle_to_dot (2s) → dot_idle
```

---

## 📁 EXPRESSION RUNTIME INTEGRATION

### Updated expressions.json Structure

```json
{
  "SYSTEM": {
    "boot_start": { "duration": 1500, "loop": false, "interruptible": false },
    "boot_progress": { "duration": 2000, "loop": true, "interruptible": false },
    "boot_complete": { "duration": 1000, "loop": false, "interruptible": true },
    "idle_to_dot": { "duration": 2000, "loop": false, "interruptible": true },
    "dot_idle": { "duration": 0, "loop": true, "interruptible": true },
    "intro_from_dot_1": { "duration": 1500, "loop": false, "interruptible": false },
    "intro_from_dot_2": { "duration": 1500, "loop": false, "interruptible": false },
    "intro_from_dot_3": { "duration": 1500, "loop": false, "interruptible": false },
    "stretch_1min": { "duration": 500, "loop": false, "interruptible": true },
    "stretch_2min": { "duration": 800, "loop": false, "interruptible": true },
    "goodbye": { "duration": 2000, "loop": false, "interruptible": false },
    "shutdown": { "duration": 1500, "loop": false, "interruptible": false }
  },
  "SPEECH": {
    "wake_detected": { "duration": 500, "loop": false, "interruptible": true },
    "listening_active": { "duration": 1000, "loop": true, "interruptible": true },
    "listening_pulse": { "duration": 300, "loop": true, "interruptible": true },
    "processing_command": { "duration": 800, "loop": false, "interruptible": true },
    "understanding": { "duration": 500, "loop": false, "interruptible": true }
  },
  "EXECUTION": {
    "executing_general": { "duration": 1000, "loop": true, "interruptible": true },
    "executing_file": { "duration": 1000, "loop": true, "interruptible": true },
    "executing_browser": { "duration": 1000, "loop": true, "interruptible": true },
    "executing_app": { "duration": 1000, "loop": true, "interruptible": true },
    "executing_calendar": { "duration": 1000, "loop": true, "interruptible": true },
    "executing_clipboard": { "duration": 500, "loop": true, "interruptible": true },
    "executing_search": { "duration": 1000, "loop": true, "interruptible": true },
    "executing_system": { "duration": 1000, "loop": true, "interruptible": true }
  },
  "RESULT": {
    "task_success": { "duration": 1500, "loop": false, "interruptible": false },
    "task_partial": { "duration": 1200, "loop": false, "interruptible": true },
    "task_failed": { "duration": 1500, "loop": false, "interruptible": true },
    "task_blocked": { "duration": 1000, "loop": false, "interruptible": true },
    "waiting_for_confirm": { "duration": 1000, "loop": true, "interruptible": true },
    "confirming": { "duration": 800, "loop": false, "interruptible": true }
  },
  "IDLE": {
    "idle_normal": { "duration": 0, "loop": true, "interruptible": true },
    "idle_happy": { "duration": 0, "loop": true, "interruptible": true },
    "idle_curious": { "duration": 0, "loop": true, "interruptible": true },
    "idle_waiting": { "duration": 0, "loop": true, "interruptible": true },
    "idle_blink": { "duration": 200, "loop": true, "interruptible": true }
  }
}
```

---

## 🎯 IDLE TIMER STATE MACHINE

```
IDLE_TIMER States:
├── IDLE_NORMAL (0-60s)
│   └── → idle_normal
├── IDLE_60s (60-120s)
│   └── → stretch_1min (at 60s)
│   └── → idle_normal
├── IDLE_120s (120s)
│   └── → idle_to_dot
│   └── → DOT_IDLE
└── DOT_IDLE (in system tray)
    └── → WAKE_TRIGGER
    └── → intro_from_dot_1/2/3 (random selection)
```

---

## 🎨 DELIVERABLES SUMMARY

### Total Animations Required: 47

| Category | Count | Animations |
|----------|-------|------------|
| System | 13 | boot_start, boot_progress, boot_complete, idle_to_dot, dot_idle, intro_from_dot_1/2/3, stretch_1min, stretch_2min, goodbye, shutdown |
| Speech | 5 | wake_detected, listening_active, listening_pulse, processing_command, understanding |
| Execution | 8 | executing_general, executing_file, executing_browser, executing_app, executing_calendar, executing_clipboard, executing_search, executing_system |
| Result | 6 | task_success, task_partial, task_failed, task_blocked, waiting_for_confirm, confirming |
| Idle | 5 | idle_normal, idle_happy, idle_curious, idle_waiting, idle_blink |

### Frame Specifications
- **FPS:** 14
- **Frames per animation:** 14 (1 second base)
- **Extended animations:** 21 frames (1.5s)
- **Looping animations:** 7 frames seamlessly looped

---

*Generated for VIZZU AI Companion - 2026*
