# CHITTI V2 — CHARACTER EVENT CONTRACT FREEZE

## 1. Executive Summary
This document freezes all canonical Character Platform Event Contracts. Future runtimes SHALL consume these exact event names. No future sprint may rename them.

---

## 2. Frozen Canonical Events

| Event Name | Description | Payload Schema |
| :--- | :--- | :--- |
| `CharacterShown` | Emitted when Character Window becomes visible on desktop | `{ timestamp, x, y, dock_edge, scale }` |
| `CharacterHidden` | Emitted when Character Window is hidden | `{ timestamp }` |
| `PresenceDotShown` | Emitted when Character transforms into Presence Dot | `{ timestamp, x, y }` |
| `PresenceDotHidden` | Emitted when Presence Dot is hidden | `{ timestamp }` |
| `ConversationPaused` | Emitted when conversation state pauses | `{ timestamp, pause_reason, narration_offset }` |
| `ConversationResumed` | Emitted when conversation resumes | `{ timestamp, narration_offset }` |
| `ConversationCompleted` | Emitted when conversation completes | `{ timestamp, conversation_id }` |
| `WakeStarted` | Emitted when wake sequence initiates | `{ timestamp, wake_source, input_mode }` |
| `WakeCompleted` | Emitted when wake sequence finishes restoring UI | `{ timestamp, restored_state }` |
| `WindowDocked` | Emitted when Character Window docks to screen edge or widget | `{ timestamp, dock_edge }` |
| `WindowUndocked` | Emitted when Character Window undocks | `{ timestamp }` |
| `AnchorChanged` | Emitted when Character anchor point changes | `{ timestamp, anchor_x, anchor_y }` |
| `RuntimeRestored` | Emitted when active runtime session is restored from memory | `{ timestamp, session_id, runtime_type }` |
