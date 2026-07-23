# CHITTI Boot Sequence

The startup order must be strictly deterministic. This sequence ensures foundation services are available before feature subsystems start up.

```text
Process Starts
        ↓
Configuration
        ↓
Logging
        ↓
Version
        ↓
Dependency Container (Composition Root)
        ↓
Event Bus
        ↓
Application Context
        ↓
Lifecycle
        ↓
Main Window
        ↓
READY
```
