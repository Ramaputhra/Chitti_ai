# CHITTI V2 — CHARACTER PLATFORM ARCHITECTURE & BOUNDARIES

## 1. Executive Summary
The **Character Platform** (`desktop/character/`) encompasses the Character Studio, Behavior Scheduler, Character Runtime, Character Scene Manager, Character Identity Platform, and Character Presence Lifecycle.

---

## 2. Architectural Boundaries & Decoupling

### Canonical Isolation Rule:
**Character Runtime SHALL NEVER directly access Capability implementations.**

Character Runtime SHALL communicate ONLY through published runtime contracts, events, and public interfaces.

Character Runtime SHALL NOT:
- Import Capability modules directly.
- Invoke Capability implementations directly.
- Depend on Capability internal classes.
- Read Capability private state.

Instead, Character Runtime SHALL consume ONLY:
- Runtime Events
- Runtime Session Contracts
- Character Anchor API
- Published Service Interfaces
- Event Bus messages

This guarantees complete decoupling between the Character Runtime and the Capability Platform. Future capability implementations remain 100% replaceable without requiring modifications to the Character Runtime.
