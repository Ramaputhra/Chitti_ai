# ADR 0012: Planner Never Executes Capabilities Directly

## Status
Accepted

## Context
In older architectures, planners often called the execution primitives directly. This tightly coupled reasoning to side-effects and broke testability.

## Decision
The Planner Runtime acts strictly as an intelligence router and graph generator. It determines *what* needs to be executed, *how* to sequence it, and the *parameters* for execution. It must **never** execute capabilities directly itself. 

Execution is exclusively managed by the Scheduler Runtime delegating to the Execution Runtime.

## Consequences
- The Planner remains stateless and purely functional (Given Context + Intent -> Output Graph).
- Execution remains isolated, observable, and fully sandboxable.
- Deterministic capabilities bypass the LLM planner entirely.
