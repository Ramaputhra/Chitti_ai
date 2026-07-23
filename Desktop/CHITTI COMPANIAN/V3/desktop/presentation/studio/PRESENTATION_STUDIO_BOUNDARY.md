# CHITTI V2 — PRESENTATION STUDIO & CHARACTER STUDIO BOUNDARY SPECIFICATION

## 1. Executive Summary
This document defines the strict architectural boundary between the **Presentation Platform** (`desktop/presentation/`) and the **Character Platform** (`desktop/character/`).

Presentation Studio and Character Studio maintain complete separation of concerns. Presentation Studio is strictly dedicated to UI rendering, data visualization, and page layouts, while Character Studio owns physical avatars, voice models, personality traits, and behavioral animations.

---

## 2. Platform Responsibilities Matrix

| Domain Category | Presentation Platform Responsibility | Character Platform Responsibility |
|---|---|---|
| **Primary Domain** | UI Layouts, Data Visualization, Document Formats | Avatar Persona, Expression, Voice & Behavior |
| **Owned Assets** | Executive Dashboards, Modern Dashboards, Glass Dashboards | 3D Avatar Mesh Models (`.glb`), Voice Models, Emotion Mappings |
| **Components** | Widgets, Charts (Bar, Line, Pie), Maps, Timelines, Tables, Stat Cards | Facial Blends, Lip Sync Phonemes, Eye Tracking, Head Nods |
| **Styling & Theme** | CSS Modules, Custom Color Variables, Typography Scales | Shader Profiles, Lighting Effects, Render Pipelines |
| **Behavior States** | Page Transitions, Grid Layout Resizing, Theme Toggles | Wake, Greeting, Listening, Thinking, Talking, Working, Celebration |
| **Prompt Templates** | Narrative Content Layout Templates (`.md`) | Conversational Persona Guidelines & System Instructions |

---

## 3. Communication Protocol & Event Bus Decoupling

1. **Presentation Runtime Isolation:** `PresentationRuntime` SHALL NEVER directly invoke avatar animations, 3D rendering pipelines, or TTS audio playback engines.
2. **EventBus Subscriptions:** `CharacterRuntime` SHALL subscribe to narration lifecycle events published by the system EventBus:
   - `NARRATION_STARTED` $\rightarrow$ Triggers Character Talking animation state and Lip Sync engine.
   - `NARRATION_FINISHED` $\rightarrow$ Triggers Character Idle state.
   - `WORKFLOW_EXECUTING` $\rightarrow$ Triggers Character Thinking / Working animation state.
   - `WORKFLOW_COMPLETED` $\rightarrow$ Triggers Character Celebration / Success gesture.

---

## 4. Future Character Studio Repository Structure (Documentation Only)

The future Character Studio will reside at `desktop/character/studio/` with the following structural layout:

```
desktop/character/
└── studio/
    └── assets/
        ├── avatars/
        │   ├── 3d_models/
        │   ├── textures/
        │   └── materials/
        ├── expressions/
        │   ├── happy.json
        │   ├── thinking.json
        │   ├── attentive.json
        │   └── neutral.json
        ├── gestures/
        │   ├── nod.json
        │   ├── wave.json
        │   └── open_palm.json
        ├── personalities/
        │   ├── assistant.json
        │   ├── friendly.json
        │   └── professional.json
        ├── voice/
        │   ├── audio_profiles/
        │   └── tts_configs/
        ├── lipsync/
        │   ├── visemes/
        │   └── phoneme_mappings/
        ├── idle/
        ├── listening/
        ├── thinking/
        ├── talking/
        ├── working/
        ├── greeting/
        ├── celebration/
        └── transitions/
```

*Note: The above directory layout is documented for architecture compliance. No implementation files have been created in `desktop/character/studio/` during Sprint 33.*
