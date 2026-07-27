# VIZZU Avatar Expressions - Graphic Designer Specification

## 📐 Technical Requirements
- **Format:** PNG sequences
- **Duration:** 1 second per expression (variable min_duration per state)
- **Frame Rate:** 14 FPS (14 frames per expression)
- **Resolution:** 512x512px recommended (scalable)
- **Naming:** `ExpressionName_001.png` to `ExpressionName_014.png`

---

## 🎭 COMPLETE EXPRESSIONS LIST (21 States from expressions.json)

These are the canonical expressions defined in `desktop/runtimes/expression/expressions.json`:

| # | Expression | Duration | Interruptible | Description |
|---|-----------|----------|---------------|-------------|
| 1 | `Idle` | 0ms (loop) | Yes | Default waiting state, slow random panning |
| 2 | `Ready` | 500ms | Yes | Alert and prepared |
| 3 | `Listening` | 500ms | Yes | Active listening, looking up |
| 4 | `Talking` | 100ms | Yes | Speaking, head tilt |
| 5 | `Thinking` | 600ms | Yes | Processing, looking up |
| 6 | `Understanding` | 300ms | Yes | Comprehending |
| 7 | `Working` | 500ms | Yes | Task in progress, jitter motion |
| 8 | `Reading` | 500ms | Yes | Reading content, scan left-right |
| 9 | `Writing` | 500ms | Yes | Writing content, scan left-right |
| 10 | `Monitoring` | 1000ms | Yes | Observing, slow panning |
| 11 | `Waiting` | 500ms | Yes | Patient pause |
| 12 | `Success` | 1200ms | No | Task complete, nod head |
| 13 | `Failure` | 1500ms | Yes | Task failed, shake head |
| 14 | `Error` | 2000ms | Yes | System error, shake head |
| 15 | `Starting` | 1000ms | No | Boot up sequence |
| 16 | `Offline` | 0ms | No | Hidden, head down |
| 17 | `Sleeping` | 0ms (loop) | Yes | Dormant mode, hidden |
| 18 | `Goodbye` | 1500ms | No | Shutting down, head down |
| 19 | `Exercising` | 0ms (loop) | Yes | Bouncing motion |

---

## 🎬 SPEECH STATES (Pipeline States - 6)

Correspond to VAD → STT pipeline:

| State | Expression | Duration | Description |
|-------|-----------|----------|-------------|
| `SLEEPING` | `Sleeping` | 0ms | Dormant, minimal presence |
| `WAKE_DETECTED` | `Starting` | 1000ms | Wake word just detected |
| `LISTENING` | `Listening` | 500ms | Actively capturing audio |
| `UNDERSTANDING` | `Understanding` | 300ms | Processing speech |
| `THINKING` | `Thinking` | 600ms | Executing task |
| `EXPECTING_REPLY` | `Waiting` | 500ms | Awaiting user response |

---

## 🏠 PRESENCE STATES (Desktop Lifecycle - 8)

| State | Expression | Description |
|-------|-----------|-------------|
| `ACTIVE` | `Ready` | Full interaction mode |
| `FOLLOW_UP_WINDOW` | `Success` | Showing results |
| `TASK_EXECUTION` | `Working` | Working on task |
| `EDGE_DOCKED_WORKING` | `Monitoring` | Minimized, active |
| `EDGE_DOCKED_IDLE` | `Idle` | Docked, waiting |
| `RELAXED_IDLE` | `Waiting` | Extended idle |
| `GOODBYE` | `Goodbye` | Shutting down |
| `RESIDENT_MODE` | `Sleeping` | Background mode |

---

## 🔊 SOUND EFFECTS (8)

| Sound | Trigger | Duration |
|-------|---------|----------|
| `success_chime.wav` | Success state | ~1.2s |
| `error_buzz.wav` | Error/Failure states | ~0.5s |
| `listening_blip.wav` | Listening state | ~0.3s |
| `task_started.wav` | Working state | ~0.3s |
| `wake_sound.wav` | Starting state | ~1s |
| `shutdown_sound.wav` | Goodbye state | ~1.5s |
| `notification.wav` | New info | ~0.3s |
| `idle_ambient.wav` | Idle background | loop | |

---

## 📁 Folder Structure

```
assets/avatar/
├── expressions/
│   ├── Idle/
│   │   ├── manifest.json
│   │   └── Idle_001.png ... Idle_014.png
│   ├── Ready/
│   ├── Listening/
│   ├── Talking/
│   ├── Thinking/
│   ├── Understanding/
│   ├── Working/
│   ├── Reading/
│   ├── Writing/
│   ├── Monitoring/
│   ├── Waiting/
│   ├── Success/
│   ├── Failure/
│   ├── Error/
│   ├── Starting/
│   ├── Offline/
│   ├── Sleeping/
│   ├── Goodbye/
│   └── Exercising/
└── sounds/
    ├── success_chime.wav
    ├── error_buzz.wav
    ├── listening_blip.wav
    ├── task_started.wav
    ├── wake_sound.wav
    ├── shutdown_sound.wav
    ├── notification.wav
    └── idle_ambient.wav
```

---

## 📋 manifest.json Template

```json
{
  "id": "Thinking",
  "fps": 14,
  "loop": false,
  "duration": 600,
  "interruptible": true,
  "category": "processing",
  "tags": ["cognitive", "analyzing"],
  "servo_motion": "look_up_and_center"
}
```

---

## 🎨 Design Guidelines

### Animation Style
- **Type:** 2D stylized robot avatar or 3D rendered character
- **Eyes:** Large, expressive - primary communication channel
- **Mouth:** Simple morphable shapes
- **Colors:** Soft blue (#4A90D9) primary, teal accents

### Frame-by-Frame Structure
- Frame 1-3: Rest/neutral position
- Frame 4-10: Peak expression
- Frame 11-14: Return to neutral or hold

### Looping Animations (Idle, Sleeping, Exercising)
- Frame 1-7: First half
- Frame 8-14: Repeat frames 1-7 seamlessly

---

## ✅ Deliverables Checklist (19 Expressions + 8 Sounds)

### Core Expressions (19)
| # | Expression | Frames | Loop |
|---|-----------|--------|------|
| 1 | Idle | 14 | Yes |
| 2 | Ready | 14 | No |
| 3 | Listening | 14 | No |
| 4 | Talking | 14 | No |
| 5 | Thinking | 14 | No |
| 6 | Understanding | 14 | No |
| 7 | Working | 14 | No |
| 8 | Reading | 14 | No |
| 9 | Writing | 14 | No |
| 10 | Monitoring | 14 | No |
| 11 | Waiting | 14 | No |
| 12 | Success | 14 | No |
| 13 | Failure | 14 | No |
| 14 | Error | 14 | No |
| 15 | Starting | 14 | No |
| 16 | Offline | 14 | No |
| 17 | Sleeping | 14 | Yes |
| 18 | Goodbye | 14 | No |
| 19 | Exercising | 14 | Yes |

### Sound Effects (8)
- [ ] success_chime.wav
- [ ] error_buzz.wav
- [ ] listening_blip.wav
- [ ] task_started.wav
- [ ] wake_sound.wav
- [ ] shutdown_sound.wav
- [ ] notification.wav
- [ ] idle_ambient.wav

---

*Generated for VIZZU AI Companion - 2026*
*Source: desktop/runtimes/expression/expressions.json*
