# Performance Review

## Overview
Analyzes blocking operations, synchronous bottlenecks, and memory footprint.

## Findings

### Finding 1: Synchronous JSON Loading on Initialization
* **Severity:** Low
* **Description:** Runtimes load JSON configurations synchronously during `initialize()`.
* **Impact:** Negligible for current scale, but reading thousands of intents synchronously could introduce a 1-2 second blocking delay during startup.
* **Recommended Fix:** Use `aiofiles` for async JSON loading.
* **Affected Files:** `desktop/intent/registry.py`, `desktop/intent/normalizer.py`
* **Estimated Refactoring Cost:** 1 hour

### Finding 2: Unbounded In-Memory Caching
* **Severity:** Medium
* **Description:** The `SpeechRuntime` and `IntentRuntime` do not cap the size of dictionaries they build in memory.
* **Impact:** Long-running sessions could theoretically degrade if logs or event caches leak.
* **Recommended Fix:** Implement LRU caching for any historical data retained.
* **Affected Files:** `desktop/intent/runtime.py`
* **Estimated Refactoring Cost:** 1 hour
