# Architecture Compliance Report

## Overview
Evaluates the codebase against the `CHITTI_ARCHITECTURE.md` and `ENGINEERING_RULES.md`.

## Findings

### Finding 1: Dependency Injection Bypass
* **Severity:** High
* **Description:** Both the `SpeechRuntime` and `IntentRuntime` accept a `config_dir: Path` in their constructors and instantiate their own dependencies internally (e.g., `TextNormalizer`, `LocalIntentRegistry`).
* **Impact:** Violates Rule 2 (Dependency Injection) and makes unit testing difficult as dependencies cannot be easily mocked.
* **Recommended Fix:** Pass instances of `ITextNormalizer`, `IIntentRegistry`, etc., via the `DIContainer` into the runtime constructors.
* **Affected Files:** `desktop/intent/runtime.py`, `desktop/app.py`
* **Estimated Refactoring Cost:** 3 hours

### Finding 2: Cooperative Cancellation Missing
* **Severity:** High
* **Description:** `IRuntime` methods like `handle_speech_transcribed` are declared `async` but do not accept an `asyncio.CancellationToken`.
* **Impact:** Violates Rule 41. If the supervisor needs to stop a runtime, it cannot interrupt an active processing loop safely.
* **Recommended Fix:** Update the `IEventBus` and `IRuntime` signatures to propagate cancellation tokens.
* **Affected Files:** `desktop/core/runtime.py`, `desktop/core/supervisor.py`
* **Estimated Refactoring Cost:** 4 hours

### Finding 3: Intent ID Immutability Enforcement
* **Severity:** Medium
* **Description:** Intent IDs are declared immutable in documentation, but the Python `IntentDefinition` dataclass is mutable.
* **Impact:** A downstream runtime could theoretically mutate an Intent ID before passing it along.
* **Recommended Fix:** Make `IntentDefinition` and `IntentRecognized` frozen dataclasses (`@dataclass(frozen=True)`).
* **Affected Files:** `desktop/intent/models.py`
* **Estimated Refactoring Cost:** 1 hour
