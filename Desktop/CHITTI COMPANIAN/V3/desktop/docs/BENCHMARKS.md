# Cognitive Benchmarks

Benchmarks are the primary mechanism for proving that the cognitive architecture works and verifying that refactoring efforts have not damaged the system.

## Rule 237: No Runtimes Without Jobs
Every runtime must be verified by a benchmark.

## Rule 238: Full Spine
Every benchmark must execute the full cognitive spine, from `User Goal` through `ExecutionRuntime` to `GoalAssessment`. Benchmarks may not bypass runtimes to test individual functions in isolation.

## Registered Benchmarks

### 001 - Find File
**Goal:** Locate `ABCD.pdf` on the filesystem.
**Required Capabilities:** `Filesystem.Search`
**Status:** PASS
