# Cognitive Architecture

This document describes the frozen architecture (Phases L and M) that powers CHITTI. It is a strictly deterministic pipeline that operates purely on immutable domain contracts.

## The Cognitive Spine

```text
User Goal
    ↓
GoalContext (Context Builder)
    ↓
Plan (Planner Runtime)
    ↓
Workflow (Workflow Translator)
    ↓
ExecutionEvents (Execution Runtime)
    ↓
WorkflowAssessment (Workflow Evaluator)
    ↓
GoalAssessment (Goal Evaluator)
```

## Architectural Principles

1. **Transformations are Pure:** Runtimes (like Planner, Translator, Evaluator) are pure functions. They consume an immutable model and output an immutable model. They do not have side effects.
2. **Execution is Isolated:** The `ExecutionRuntime` is the only component that touches the real world via Capabilities.
3. **Communication via EventBus:** Components do not call each other directly. They subscribe and publish to the EventBus, making the system 100% observable.
4. **Referential Transparency:** Given the same Workflow, execution must produce the identical sequence of ExecutionEvents.
