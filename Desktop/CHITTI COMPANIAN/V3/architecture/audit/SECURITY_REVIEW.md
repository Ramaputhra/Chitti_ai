# Security Review

## Overview
Analyzes authentication, permission boundaries, and policy enforcement.

## Findings

### Finding 1: Policy Enforcement Delegation
* **Severity:** High
* **Description:** The Intent Runtime currently marks intents with `requires_authentication` but does not enforce it. 
* **Impact:** If Phase 4 relies entirely on the Planner to respect this flag, a bug in the Planner could execute unauthorized intents.
* **Recommended Fix:** Implement a strict `PolicyInterceptor` on the EventBus that explicitly drops or pauses events marked `requires_authentication: True` if the session context lacks a `SpeakerVerified` flag.
* **Affected Files:** `desktop/core/supervisor.py` (EventBus logic)
* **Estimated Refactoring Cost:** 3 hours

### Finding 2: Lack of Event Source Validation
* **Severity:** Medium
* **Description:** Any module can theoretically publish `SpeakerVerified`.
* **Impact:** A compromised plugin could fake authentication.
* **Recommended Fix:** EventBus must validate that security-sensitive events are published exclusively by the `SpeechRuntime` or `PolicyEngine`.
* **Affected Files:** `desktop/core/supervisor.py`
* **Estimated Refactoring Cost:** 2 hours
