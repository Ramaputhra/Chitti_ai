# Repository Ownership & Governance

This document establishes clear boundaries and ownership across the CHITTI repository. It exists to prevent architectural drift, duplicate structures, and circular dependencies.

## Module Ownership

| Subsystem     | Owner          | Responsibility                                  |
| ------------- | -------------- | ----------------------------------------------- |
| product       | UX             | User-facing experience, automation, UI, signals |
| brain         | Cognition      | Core reasoning and decision-making              |
| platform      | Infrastructure | Shared systems, event bus, integrations         |
| models        | Domain         | Shared schemas and immutable contracts          |
| capabilities  | Actions        | External software and hardware operations       |
| resources     | Shared Assets  | Prompts, templates, HTML, sounds, UI icons      |
| benchmarks    | QA             | Cognitive verification and jobs                 |
| tests         | QA             | Unit, regression, and integration testing       |
| docs          | Documentation  | System-level documentation and standards        |

## Governance Rules

### 1. Top-Level Directory Creation Rule
**A new top-level folder may only be created if its responsibility cannot be expressed within an existing owner.** If a subsystem naturally belongs to Product, Brain, Platform, Models, Capabilities, Resources, Benchmarks, Tests, or Docs, it must be placed there. Creating a new top-level directory requires an explicit architectural decision and documented justification.

### 2. Dependency Direction Rule
To prevent circular dependencies and maintain architectural stability, dependencies must flow strictly in one direction:

- **Allowed:** `Product` -> `Brain`
- **Allowed:** `Product` -> `Capabilities`
- **Allowed:** `Brain` -> `Models`
- **Allowed:** `Brain` -> `Platform`
- **Allowed:** `Capabilities` -> `Platform`
- **Allowed:** `Capabilities` -> `Models`
- **Allowed:** `Platform` -> `Models`

- **Forbidden:** `Models` -> anything
- **Forbidden:** `Platform` -> `Product`
- **Forbidden:** `Brain` -> `Product`
- **Forbidden:** `Models` -> `Brain`
- **Forbidden:** `Models` -> `Capabilities`

*Models are the foundation. Everything else depends on them. Nothing inside Models depends upward.*
