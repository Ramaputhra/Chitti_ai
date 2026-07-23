# Technical Debt Report

## Overview
Identifies shortcuts taken during Phase 0-3 that must be addressed before entering production.

## Findings

### Finding 1: Mock Metadata and Hardcoded Assumptions
* **Severity:** Medium
* **Description:** The Intent Runtime Registry currently mocks metadata (e.g., hardcoding `requires_authentication=True`) instead of reading it from a dedicated schema or fully trusting the JSON.
* **Impact:** As the number of intents grows, this will cause inconsistent behavior.
* **Recommended Fix:** Implement a strict `marshmallow` or `pydantic` schema validator for all JSON files, forcing them to supply required metadata fields.
* **Affected Files:** `desktop/intent/registry.py`
* **Estimated Refactoring Cost:** 2 hours

### Finding 2: Incomplete Error Propagation
* **Severity:** Medium
* **Description:** When `IntentUnknown` is emitted, there is no standardized way to trace it back to the exact component that dropped the intent (Matcher vs Validator).
* **Impact:** Debugging false negatives will be difficult.
* **Recommended Fix:** Add a `drop_reason` string to `IntentUnknown` events.
* **Affected Files:** `desktop/intent/models.py`, `desktop/intent/runtime.py`
* **Estimated Refactoring Cost:** 1 hour
