# CHITTI V2 — WINDOW SYSTEM SPECIFICATION

## 1. Canonical Window Types & IDs
- `UI_WINDOW_CHARACTER_WIDGET`
- `UI_WINDOW_NOTIFICATION`
- `UI_WINDOW_DIALOG`
- `UI_WINDOW_FLOATING`
- `UI_WINDOW_OVERLAY`
- `UI_WINDOW_EDGE`
- `UI_WINDOW_POPUP`
- `UI_WINDOW_SYSTEM`
- `UI_WINDOW_DEBUG`

## 2. Semantic Layer Ordering
- `CHARACTER` (Priority 100)
- `CHARACTER_WIDGET` (Priority 200)
- `FLOATING_WIDGET` (Priority 300)
- `NOTIFICATION` (Priority 400)
- `DIALOG` (Priority 500)
- `SYSTEM_OVERLAY` (Priority 600)
- `DEBUG` (Priority 700)

## 3. Generic Attachment API Contracts
- `attach()`, `detach()`, `move()`, `follow()`, `release()`, `update_anchor()`.
