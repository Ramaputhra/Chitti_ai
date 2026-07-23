# CHITTI Development Constitution

## Version 1.0 (Frozen)

---

# Purpose

This document governs **all future development** of CHITTI Desktop Companion.

The architecture has been completed and frozen.

Future development focuses exclusively on implementing product capabilities defined in `PRODUCT_V1_ROADMAP.md`.

This document exists to ensure the project **never derails again**.

---

# PART 1 — Architecture Freeze

## Rule 1

The following core architecture is permanently frozen.

* Brain
* Planner
* Voice Runtime
* Presence Runtime
* Time Runtime
* Awareness Runtime
* Memory Runtime
* Inference Runtime
* Session Runtime
* Desktop Automation Runtime
* Event Bus

No sprint may redesign them.

---

## Rule 2

No new Runtime may be introduced.

Exception:

Only if explicitly approved by the User.

---

## Rule 3

No sprint may redesign existing architecture.

Enhancement is allowed.

Replacement is prohibited.

---

# PART 2 — Sprint Rules

## Rule 4

Only ONE sprint may be active.

Never work on multiple roadmap sprints.

---

## Rule 5

A sprint must finish completely before the next begins.

No partially completed sprint may be skipped.

---

## Rule 6

Every sprint must correspond to ONE capability group in

```
PRODUCT_V1_ROADMAP.md
```

Never invent new sprint themes.

---

## Rule 7

Every sprint must produce at least one visible user experience.

If the user cannot demonstrate it,

the sprint is incomplete.

---

# PART 3 — Before Starting Every Sprint

Before implementation Antigravity MUST perform the following checklist.

```
□ Read PRODUCT_V1_ROADMAP.md

□ Find first unfinished capability

□ Verify it belongs to current phase

□ Verify no earlier capability remains unfinished

□ Confirm no architecture modification is proposed

□ Present Sprint Plan

□ Wait for User Approval
```

If any check fails

STOP.

---

# PART 4 — During Sprint

Antigravity may

✅

Implement

Refactor internally

Improve performance

Write tests

Fix bugs

Improve UX

Improve reliability

---

Antigravity may NOT

❌

Create new Runtime

Create new Architecture

Replace Event Bus

Replace Planner

Replace Memory

Replace Awareness

Replace Sessions

Replace Inference

Replace Voice

Move folders without reason

Rename major systems

Invent new abstraction layers

Introduce speculative future systems

---

# PART 5 — After Sprint Completion

Mandatory

```
□ Run validation

□ Update PROJECT_STATUS.md

□ Update progress.md

□ Write Sprint Walkthrough

□ Tick completed roadmap items

□ Recommend ONLY next roadmap sprint
```

Never recommend

Sprint +2

Sprint +5

Random feature

Architecture improvement

---

# PART 6 — Derailment Detection

Immediately STOP and warn the User if implementation attempts to:

---

### Warning Type A

Architecture Drift

Example

"I think we need another Runtime."

STOP.

---

### Warning Type B

Scope Creep

Example

"We're building Browser Intelligence but should also redesign Memory."

STOP.

---

### Warning Type C

Sprint Jumping

Example

Current sprint

121

Proposed work

126

STOP.

---

### Warning Type D

Feature Injection

Example

"This would be cool..."

Not in roadmap.

STOP.

---

### Warning Type E

Framework Rebuild

Example

"Let's rewrite Planner."

STOP.

---

### Warning Type F

AI Overengineering

Example

"We should build an Agent Framework."

STOP.

---

### Warning Type G

Premature Optimization

Example

"We should replace SQLite."

STOP.

---

# PART 7 — Definition of Done

A sprint is COMPLETE only when

```
□ Planned capability implemented

□ Manual demo succeeds

□ Existing tests pass

□ No regressions

□ Architecture unchanged

□ Documentation updated

□ Roadmap updated

□ Walkthrough written
```

Otherwise

Sprint remains ACTIVE.

---

# PART 8 — Roadmap Authority

`PRODUCT_V1_ROADMAP.md`

is the

ONLY

source of product planning.

If a feature does not exist there

it does not exist.

---

# PART 9 — Roadmap Execution Algorithm

Antigravity must execute this algorithm forever.

```
START

↓

Read PRODUCT_V1_ROADMAP.md

↓

Locate first unfinished capability

↓

Generate Sprint Plan

↓

Wait for approval

↓

Implement

↓

Validate

↓

Update documentation

↓

Mark capability complete

↓

Recommend ONLY next unfinished capability

↓

Repeat
```

Never deviate.

---

# PART 10 — Feature Enhancement Rule

After every roadmap capability reaches **100%**, Antigravity may propose enhancement sprints **only** if all of the following are true:

1. The enhancement builds on an existing completed capability.
2. It introduces **no new architecture**.
3. It is presented as an optional enhancement after the roadmap sprint is complete.
4. The user explicitly approves it before implementation.

This ensures enhancements never interrupt core roadmap completion.

---

# PART 11 — Recovery Rule

If development ever becomes uncertain:

STOP.

Do not code.

Do not redesign.

Do not guess.

Instead:

1. Read `PRODUCT_V1_ROADMAP.md`.
2. Read this Constitution.
3. Determine the current active sprint.
4. Resume from the **first unfinished roadmap item**.

No alternative recovery process is permitted.

---

# Final Principle

> **CHITTI is a product, not a research project.**
>
> The architecture is complete. Intelligence emerges by composing the existing systems, not by inventing new ones. Every sprint must make CHITTI more useful to the user, never more complicated internally.
