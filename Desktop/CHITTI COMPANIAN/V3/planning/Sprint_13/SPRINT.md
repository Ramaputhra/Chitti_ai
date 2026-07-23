# Sprint 13: Personal Intelligence Runtime

## 1. Goal
Complete Milestone E (Personal Intelligence). Establish the subjective memory and profiling systems (Identity, Preference, Behavior). Introduce Signals, Scoring Engines, and the `Memory` model. Ensure graceful memory degradation via the Forgetting Engine.

## 2. Deliverables
- `IdentityProfile`, `PreferenceProfile`, `BehaviorProfile` models & `ProfileManager`.
- `ImportanceEngine`, `HabitEngine`, and `PersonalIntelligenceScoreEngine`.
- `Memory` model with reserved categories.
- `MemoryManager` and `ForgettingEngine` (Active -> Dormant -> Archived -> Compressed -> Pruned).
- `ContextManager`.
