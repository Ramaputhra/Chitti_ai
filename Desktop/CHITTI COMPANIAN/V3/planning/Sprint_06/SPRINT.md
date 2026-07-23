# Sprint 6: Voice Runtime

## 1. Goal
Establish the physical conversational lifecycle bridging audio, sessions, and interrupts. 
Deliverables include the Conversation Session, Audio State Machine, Wake Word mock integration, Interrupt management with priority rules, Latency tracking, and exporting session data to disk.

## 2. Deliverables
- Audio State Machine (OFF -> IDLE -> WAKE_DETECTED -> ...)
- IWakeWordProvider and MockWakeWord
- Conversation Session & Latency Tracker
- Interrupt Manager (reasons: USER, SYSTEM, TIMEOUT, etc.)
- Voice Focus Manager
- Session Recorder (saving JSON logs to disk)
- Developer Console Session Inspector
- Advanced YAML Scenarios for Session Control

## 3. Core Rule
- Only ONE active ConversationSession may exist at a time. Double wakes will be explicitly defined (e.g., ignored if actively responding).
