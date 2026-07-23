# Capability Matrix

This dashboard tracks the product-level maturity of the CHITTI Companion system across all disciplines.

| Capability               | Status | Notes |
| ------------------------ | ------ | ----- |
| Configuration            | ✅      | Persistent JSON |
| Logging                  | ✅      | Abstracted `ILoggingService` |
| Event Bus                | ✅      | In-memory pub/sub |
| Runtime Services         | ✅      | Unified DI & orchestrator |
| Audio Capture            | ✅      | PortAudio + sounddevice |
| Voice Activity Detection | ✅      | Energy RMS algorithm |
| Audio Buffering          | ✅      | Emits Voice.AudioReady |
| STT Interface            | ✅      | Mocked implementations |
| Context Engine           | ✅      | Aggregates context via DI |
| Intent Engine            | ✅      | Dataclass driven parsing |
| Action Planner           | ✅      | Generates Workflows |
| Skills (Response)        | ✅      | ResponseBuilder mock |
| Memory                   | ⏳      | Future Sprint |
| Emotion                  | ⏳      | Future Sprint |
| Desktop Automation       | ⏳      | Future Sprint |
| Mail                     | ⏳      | Future Sprint |
| Hardware Integration     | ⏳      | Future Sprint |
