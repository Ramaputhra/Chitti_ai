# CHITTI V2 — UNIFIED TIMELINE MODEL

## 1. Overview
The **Timeline Model** (`timeline_scheduler.py`) aggregates timeline streams from all independent runtimes into a unified chronological sequence.

## 2. Merged Timeline Streams
1. **Speech Timeline:** Speech start, audio duration, sentence boundaries, speech end.
2. **Character Timeline:** Behavior transitions, eye blinks, gestures, animations.
3. **Widget Timeline:** Widget open, expand, dock, state update, collapse, close.
4. **Presentation Timeline:** Slide transitions, narration timing, laser pointer.
5. **Notification Timeline:** Toast popup display, progress ticks, dismiss.
6. **Execution Timeline:** Capability workflow start, step execution, completion.
