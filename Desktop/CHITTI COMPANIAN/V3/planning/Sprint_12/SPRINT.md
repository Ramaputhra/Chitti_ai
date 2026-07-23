# Sprint 12: Semantic Runtime

## 1. Goal
Complete Milestone D (Knowledge) by building the Semantic Runtime. This runtime enriches the Knowledge Repository by extracting Entities from Artifacts, resolving Aliases, mapping Canonical Names, and validating Relationships using a robust Provider -> Registry -> Router architecture.

## 2. Deliverables
- `Provenance` and `EntityEvidence` models.
- Frozen `Entity` model.
- `IEntityProvider`, `EntityProviderRegistry`, `SemanticRouter`.
- `EntityManager`, `AliasManager`, `CanonicalManager`, `RelationshipManager`.
- Relationship Candidate Generation and Validation pipeline.
