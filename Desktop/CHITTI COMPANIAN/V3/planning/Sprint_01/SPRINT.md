# Sprint 1: Application Foundation Contract

**Status:** IN_PROGRESS (APPROVED)

## Branch Strategy
- `main`: Stable production releases only
- `develop`: Integration branch
- `feature/<task-id>-<short-name>`: One feature per branch
- `bugfix/<task-id>`: Bug fixes
- `hotfix/<version>`: Production emergency fixes

## 1. Infrastructure
- Repository setup, build system (`uv`), strict folder structure, Config Service, Logging, Exception Handler, Constants, Version Manager.

## 2. Platform
- Event Bus, Manual DI, ApplicationContext, Lifecycle Manager.

## 3. UI Shell
- Main window layout, Theme interface.

## 4. Verification
- App launches, logs write, event bus dispatches, config loads, clean shutdown.

## 5. Deliverables
- [ ] Project builds
- [ ] Blank application launches
- [ ] Logging works
- [ ] Event Bus works
- [ ] Configuration works
- [ ] Theme switching framework exists
- [ ] Application lifecycle implemented
- [ ] Unit tests passing
- [ ] Documentation updated

## 6. Acceptance Criteria
- Startup time < 2 seconds
- Memory < 120 MB idle
- Application exits without exceptions
- Zero Ruff errors, Zero mypy errors
- 100% Sprint tasks completed
- No architecture violations

## 7. Non-Goals
This sprint will NOT include:
- AI providers, LLMs, Voice, Vision, Hardware, Cloud, DB.

## 8. Review Checklist
- Architecture, Coding Standards, Logging, Configuration, Error Handling, Tests, Documentation, Performance.
- No duplicated code, no TODOs, no temporary hacks.

## 9. Failure Criteria
Sprint fails if: Application crashes, config cannot load, event bus unreliable, circular imports detected, global mutable state introduced, architecture violated, docs incomplete, tests fail.

## 10. Exit Criteria
- Allowed to edit: `desktop/`, `pyproject.toml`, `README.md`, `tests/`.
- Forbidden: `firmware/`, `hardware/`, `planning/`, `architecture/`, `engineering_rules.md`.
- **Sprint 2 may not begin until Sprint 1 is Approved, Merged, and Frozen.**

## 11. Definition of Done
A task is Done only if:
- [ ] Code implemented
- [ ] Unit tests added
- [ ] Static analysis passes
- [ ] Documentation updated
- [ ] Logging implemented
- [ ] Error handling implemented
- [ ] No duplicated code
- [ ] Reviewed by Team Leader
- [ ] Approved by Validation Layer
- [ ] Merged into develop
- [ ] Sprint documentation updated

**Sprint Burn Rule:** No task may be started until all of its dependencies are marked COMPLETE.
