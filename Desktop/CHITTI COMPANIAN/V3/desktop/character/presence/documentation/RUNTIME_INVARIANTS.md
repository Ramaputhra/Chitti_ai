# CHITTI V2 — CHARACTER RUNTIME INVARIANTS

## 1. Executive Summary
This document records the **permanent architectural contracts and invariants** governing the CHITTI Character Platform. These rules are non-negotiable and permanently frozen.

---

## 2. Immutable Engineering Rules

1. **Visual Presence Independence:** Visual Presence visibility SHALL NEVER stop or alter Background Runtime execution. Background tasks, downloads, OCR, and memory consolidation operate independently.
2. **Widget Rendering Isolation:** Character Runtime SHALL NEVER render Widgets. All desktop widget rendering is owned exclusively by the Desktop UI Runtime.
3. **Character Window Ownership:** Desktop UI Runtime SHALL NEVER move or reposition the Character Window directly.
4. **Anchor API Contract:** Desktop UI Runtime SHALL consume the Character Anchor API (`get_character_anchor()`) ONLY when positioning character-attached widgets.
5. **Conversation Decoupling:** Conversation & Narration SHALL remain independent from Visual Presence. Hiding the window does not implicitly cancel speech unless explicitly requested by the user.
6. **Wake Engine Independence:** Wake Runtime & Hotkey Listener SHALL remain active and independent from Character visibility.
7. **Motion Token Enforcement:** All motion, animation, and physics MUST reference Motion Tokens (`desktop/shared/motion/`). No local hardcoding permitted.
8. **Character Window Specifications:** Character Window frames SHALL remain strictly `640×344` pixels, `14 FPS` playback, `RGBA PNG` format, with a `Transparent Background`.
9. **Capability Platform Decoupling:** Character Runtime SHALL NEVER directly access Capability implementations. Character Runtime SHALL communicate ONLY through published runtime contracts, events, and public interfaces. It SHALL NOT:
   - Import Capability modules directly.
   - Invoke Capability implementations directly.
   - Depend on Capability internal classes.
   - Read Capability private state.
   Instead, Character Runtime SHALL consume ONLY Runtime Events, Runtime Session Contracts, Character Anchor API, Published Service Interfaces, and Event Bus messages.
