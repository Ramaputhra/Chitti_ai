# CHITTI V2 — CANONICAL MOTION DESIGN SYSTEM

## 1. Executive Summary
The **Canonical Motion Design System** (`desktop/shared/motion/`) serves as the single source of truth for motion definitions, spring physics, timing tokens, opacity transitions, and scale tokens across the entire CHITTI platform.

---

## 2. Design Principles
Inspired by **Apple Human Interface Guidelines** and **Windows 11 Fluent Motion**:
- **Natural & Responsive:** Motion responds instantly to user interaction with soft settling springs.
- **Premium & Elegant:** Subtle overshoots without robotic/mechanical stops or game-like exaggeration.
- **Zero Local Hardcoding:** NO runtime shall hardcode animation durations, spring values, or easing curves locally. All runtimes consume Motion Tokens.

---

## 3. Core Motion Tokens & Timing

### A. Timing Tokens:
- `FAST`: 120 ms
- `NORMAL`: 180 ms
- `MEDIUM`: 240 ms
- `SLOW`: 320 ms
- `LONG`: 450 ms
- `BREATH`: 3000 ms
- `IDLE`: 5000 ms
- `SLEEP`: 8000 ms

### B. Spring Profiles:
- `Gentle`, `Responsive`, `Playful`, `Heavy`, `Elastic`, `Dock`, `Slime`, `Wake`, `Tooltip`, `Widget`, `Character`.

### C. Slime Deformation Limits:
- **Max Stretch:** 5% (`1.05`)
- **Max Compression:** 4% (`0.96`)
- **Recovery:** Spring profile (`SPRING_SLIME`).

---

## 4. Hot Reload Support
Changing any Motion Token or spring profile in `MOTION_REGISTRY` takes effect immediately for future animations without restarting the application.
