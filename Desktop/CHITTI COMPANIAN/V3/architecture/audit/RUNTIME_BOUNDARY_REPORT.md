# Runtime Boundary Report

## Overview
Evaluates isolation between runtimes.

## Findings

### Finding 1: Conversation Context Coupling
* **Severity:** Medium
* **Description:** The `IntentRuntime` requires `language` from `SpeechTranscribed`. However, it also assumes `conversation_id` and `speaker_id` will be magically available or mocked.
* **Impact:** Violates the Context Engine separation. The Intent Runtime should not maintain session state.
* **Recommended Fix:** The EventBus or a `ContextInterceptor` should attach `ContextPayload` to all events automatically, rather than hardcoding it in the Intent Runtime.
* **Affected Files:** `desktop/intent/runtime.py`
* **Estimated Refactoring Cost:** 2 hours

### Finding 2: Direct File System Access in Runtimes
* **Severity:** Medium
* **Description:** Runtimes use `Path.exists()` and `open()` directly instead of abstracting configuration behind an `IConfigProvider`.
* **Impact:** Cross-platform deployment (or packaging into binaries) will fail if config paths change.
* **Recommended Fix:** Introduce `desktop/core/config.py` and pass an `IConfigProvider` to runtimes.
* **Affected Files:** `desktop/intent/normalizer.py`, `desktop/intent/registry.py`
* **Estimated Refactoring Cost:** 2 hours
