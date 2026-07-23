# CHITTI V2 — CHARACTER PRESENCE LIFECYCLE ARCHITECTURE

## 1. Executive Summary
The **Character Presence Lifecycle** (`desktop/character/presence/`) governs visual companion visibility, state transitions, middle-click transformations, presentation mode restoration, conversation suspension modeling, and presence memory persistence.

---

## 2. Three Independent Layers
1. **Visual Presence:** Character Window, Presence Dot, System Tray.
2. **Conversation / Narration:** Voice Runtime, Speech Queue, Speech Session, Narration Composer.
3. **Background Runtime:** Capability Runtime, Background Tasks, Memory Processing, Wake Engine, Hotkey Listener.

*Design Principle:* Visual presence visibility SHALL NEVER determine or interrupt capability execution or background task processing.

---

## 3. Conversation Suspension Model
Defined in `desktop/character/presence/conversation_state.py`:
- `ACTIVE`: Conversation is actively rendering or speaking.
- `PAUSED_BY_USER`: User middle-clicked Presence Dot to pause visual & speech outputs.
- `PAUSED_SYSTEM_TRAY`: Automatically paused on entering System Tray.
- `PAUSED_FULLSCREEN` & `PAUSED_PRESENTATION`: Paused during specific fullscreen environments.
- `INTERRUPTED`: Stopped by high-priority user prompt or error.
- `COMPLETED` & `FAILED`: Session outcome states.

### Resumability Handling
When a user requests *"Continue"*, *"Resume"*, *"Keep going"*, or *"Resume previous explanation"*:
- If `resume_allowed == True`, CHITTI resumes from stored narration/speech offset (`narration_offset`, `speech_offset`, `remaining_queue`).
- If `resume_allowed == False`, CHITTI explains briefly that the capability output cannot be resumed and offers to restart or summarize.
- Never restarts from beginning automatically.

---

## 4. Expanded Presence Memory Schema (`presence_memory.json`)
Persists across application restarts:
- Desktop Position (`last_position_x`, `last_position_y`)
- Dock Edge (`last_dock_edge`)
- Monitor (`last_monitor`)
- Scale (`last_window_scale`)
- Presence State (`last_presence_state`)
- Presentation Position (`last_presentation_x`, `last_presentation_y`)
- Widget Layout (`last_widget_layout`)
- Widget Visibility (`last_widget_visibility`)
- Active Capability (`last_active_capability`)
- Active Presentation (`last_active_presentation`)
- Conversation State (`last_conversation_state`)
- Wake Source (`last_wake_source`)
- Character Scale (`last_character_scale`)
- Dock Animation (`last_dock_animation`)
- Theme (`last_theme`)
- Motion Theme (`last_motion_theme`)
- Screen Resolution (`last_screen_resolution`)
- DPI Scale (`last_dpi_scale`)
- Desktop Workspace (`last_desktop_workspace`)
- Restore Bounds (`last_restore_bounds`)

*Automatic Migration:* Legacy memory files missing any expanded fields are automatically migrated to full schema without user intervention.

---

## 5. Desktop Context Manager
`desktop_context_manager.py` detects presentation environments, fullscreen applications, games, movies, remote desktop sessions, screen sharing, multiple monitors, and desktop workspace changes.
