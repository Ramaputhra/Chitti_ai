# CHITTI V2 — GENERIC WINDOW ATTACHMENT API

## 1. Overview
The **Generic Window Attachment API** (`window_attachment.py`) provides an abstract attachment framework allowing desktop windows to bind to diverse target types without knowing widget implementations.

---

## 2. Supported Target Types
- `CHARACTER_ANCHOR`: Consumes Character Anchor API (`get_character_anchor()`) ONLY.
- `DESKTOP_COORD`: Binds to absolute screen coordinates (`x`, `y`).
- `SCREEN_EDGE`: Binds to screen edges (`top`, `bottom`, `left`, `right`).
- `MOUSE_POS`: Follows current cursor position.
- `RUNTIME_SESSION`: Binds to active capability runtime session bounds.

---

## 3. Attachment Contract Interface
- `attach(target_type, anchor_data, offset_x, offset_y)`
- `detach()`
- `move(new_x, new_y)`
- `follow()`
- `release()`
- `update_anchor(new_anchor_data)`

---

## 4. Character Decoupling Rule
Attachment to Character SHALL consume ONLY the Character Anchor API (`get_character_anchor()`). Desktop UI Runtime SHALL NEVER move Character Window, modify Character Position, or modify Character State directly.
