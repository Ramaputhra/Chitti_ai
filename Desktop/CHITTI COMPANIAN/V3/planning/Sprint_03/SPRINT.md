# Sprint 3: Audio Runtime

## 1. Goal
Build the robust OS-level audio abstraction for capturing and playing sound, including Energy-based Voice Activity Detection (VAD).

## 2. Deliverables
- Audio Models (`AudioPacket`)
- Audio Format Manager
- Audio Device Manager
- Microphone Manager
- Speaker Manager
- VAD Strategy (`EnergyVAD`)
- Audio Pipeline (Buffering)
- Audio Session (Orchestration)
- Memory and rapid start/stop tests.

## 3. Non-Goals
- No STT (Speech to Text)
- No Wake Word
- No Conversation Logic
- End boundary is `Voice.AudioReady`.
