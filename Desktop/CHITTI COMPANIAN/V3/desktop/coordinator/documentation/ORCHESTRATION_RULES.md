# CHITTI V2 — VISUAL ORCHESTRATION RULES

## 1. Priority Hierarchy
1. `CRITICAL` (1000)
2. `ERROR` (900)
3. `WARNING` (800)
4. `ACTIVE_CONVERSATION` (700)
5. `PRESENTATION` (600)
6. `MEDIA` (500)
7. `PRODUCTIVITY` (400)
8. `BACKGROUND` (300)
9. `IDLE` (100)

## 2. Yielding & Conflict Resolution
- Lower priority visuals automatically yield to higher priority visuals.
- When two requests conflict for Character Anchor or screen bounds, `ConflictResolver` selects the higher priority winner and requests the yielding target to reposition or dock.
