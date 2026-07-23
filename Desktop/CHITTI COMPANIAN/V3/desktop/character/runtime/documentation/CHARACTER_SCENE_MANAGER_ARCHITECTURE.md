# CHITTI V2 — CHARACTER SCENE MANAGER ARCHITECTURE

## 1. Executive Summary
The **Character Scene Manager** (`desktop/character/runtime/scene/`) is the highest-level orchestration component INSIDE `Character Runtime`. It determines HOW `Character Runtime` executes `BehaviorScript` according to the current runtime scene.

---

## 2. Platform Architecture & Separation
```
Behavior Scheduler -> BehaviorScript -> CharacterRuntime -> Character Scene Manager -> Behavior Timeline Compiler -> Transition Engine -> Clip Player -> Frame Player -> Renderer -> Transparent Character Window
```

- **Strict Internal Boundary:** Character Scene Manager is an INTERNAL component of Character Runtime.
- **Zero Cognition / Decision Authority:** Does NOT perform intent planning, capability selection, personality decisions, voice synthesis, speech generation, or behavior selection. `Behavior Scheduler` remains the ONLY owner of `BehaviorScript` generation.

---

## 3. Canonical Character Scenes
`BOOT`, `WAKE`, `GREETING`, `LISTENING`, `THINKING`, `TALKING`, `WORKING`, `PRESENTING`, `SEARCHING`, `NAVIGATING`, `REMINDER`, `SUCCESS`, `WARNING`, `ERROR`, `IDLE`, `SLEEP`, `EDGE_DOT`, `HIDDEN`.

---

## 4. Scene Priority Hierarchy
1. `ERROR` (Priority 7)
2. `WARNING` (Priority 6)
3. `REMINDER` (Priority 5)
4. `PRESENTING` (Priority 4)
5. `WORKING` / `NAVIGATING` / `SEARCHING` (Priority 3)
6. `TALKING` (Priority 2)
7. `IDLE` (Priority 1)

---

## 5. Scene Recovery Rules
When a high-priority scene interrupts an active scene:
1. The active lower-priority scene is pushed to `scene_stack`.
2. The high-priority scene executes.
3. Upon completion, `CharacterSceneManager` pops the stack and automatically restores the interrupted scene (e.g. `WORKING` $\rightarrow$ `REMINDER` $\rightarrow$ `WORKING`).
