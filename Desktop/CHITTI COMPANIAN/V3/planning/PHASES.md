# Phase Gates

A phase is considered complete only when:
* Every planned deliverable exists.
* Documentation is reviewed.
* Acceptance criteria are satisfied.
* No unresolved blockers remain.
* The phase is explicitly marked **Frozen**.

Only then does the next phase begin.

## PHASE 00 — Foundation
**Objective:** Freeze the project vision.
**Deliverables:** PROJECT_OVERVIEW.md, TECH_STACK.md, ENGINEERING_RULES.md, FOLDER_STRUCTURE.md, CODING_STANDARDS.md, ROADMAP.md
**Exit Criteria:** No major architectural questions remain. Technology choices are locked.

## PHASE 01 — Architecture
**Objective:** Define system structure.
**Sprints:**
* Sprint 1: System, Layered, Module boundaries
* Sprint 2: Desktop, Firmware, Hardware
* Sprint 3: AI, Communication, Deployment
**Exit Criteria:** Every subsystem has a defined place.

## PHASE 02 — Module Specifications
**Objective:** Define responsibilities only. (One sprint per major module).
**Modules:** Conversation Engine, Memory Engine, Emotion Engine, Intent Engine, Scheduler, AI Provider Layer, Voice Engine, Vision Engine, Avatar Engine, Plugin System, Hardware Manager, Settings, Notifications, Logging, Database.
**Exit Criteria:** Every module has a specification.

## PHASE 03 — Interface Contracts
**Objective:** Freeze APIs before coding. (One sprint per interface group).
**Exit Criteria:** APIs are frozen.

## PHASE 04 — Data Models
**Objective:** Define all shared data.
**Exit Criteria:** Shared data formats are frozen.

## PHASE 05 — Feature Backlog
**Objective:** Break the vision into implementable work.
**Exit Criteria:** Every planned capability exists as a backlog item.

## PHASE 06 — Use Cases
**Objective:** Describe real user interactions. (Target: 300–500 use cases).
**Exit Criteria:** Features are validated against user scenarios.

## PHASE 07 — Sprint Planning
**Objective:** Build a dependency-driven implementation roadmap.
**Rule:** A sprint must not introduce unrelated work.

## PHASE 08 — Implementation
**Sequence:** Architecture review -> Implementation -> Unit tests -> Documentation update -> Code review -> Merge.

## PHASE 09 — Integration
**Order:** Core -> Voice -> AI -> Memory -> Emotion -> UI -> Hardware -> Plugins.

## PHASE 10 — Testing
**Types:** Unit, Integration, UI, Performance, Regression, Hardware-in-the-loop, End-to-end.
**Rule:** A feature is not complete until all applicable tests pass.

## PHASE 11 — Hardware Deployment
**Objective:** Deploy only after desktop MVP is stable.
**Milestones:** ESP32 simulation -> Display -> Speaker -> Microphone -> Servos -> Basic sensors -> Custom PCB.

## PHASE 12 — Production Release
**Checklist:** Architecture audit, Security review, Performance review, Documentation complete, Installer/package generation, Release notes, Version tagging.
