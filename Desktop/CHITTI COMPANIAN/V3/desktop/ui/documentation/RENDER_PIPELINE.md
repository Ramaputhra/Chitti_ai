# CHITTI V2 — RENDER PIPELINE & PROFILES

## 1. Render Profiles (FPS Targets)

| Render Profile | Target FPS | Usage Scope |
| :--- | :--- | :--- |
| `CHARACTER` | 14 FPS | **Reserved exclusively for Character Runtime.** Desktop UI NEVER renders Character PNGs. |
| `WIDGET` | 30 FPS | Window animations, transitions, opacity, scaling, docking. |
| `WAVEFORM` | 24 FPS | Microphone audio waveform widgets. |
| `PRESENCE_DOT` | 5 FPS | Low-power idle indicator rendering. |
| `STATIC_WINDOW` | Event-Driven | Redraws ONLY when window state or content changes. |

## 2. Hardware Accelerated Composition
- GPU handles transparency, transforms, scaling, and opacity compositing.
- CPU continuous polling and busy waiting are strictly prohibited.
