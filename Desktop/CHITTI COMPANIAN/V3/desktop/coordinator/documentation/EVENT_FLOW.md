# CHITTI V2 — EVENT FLOW & SYNCHRONIZATION SPECIFICATION

## 1. Cross-Runtime Event Synchronization
Runtime events flow into `EventSynchronizer` and `SessionSynchronizer` without any runtime directly invoking another runtime.

```
Character Events ---> |
Voice Events --------> | -> EventSynchronizer -> Visual Coordinator -> Execution Events
Widget Events -------> |
```
