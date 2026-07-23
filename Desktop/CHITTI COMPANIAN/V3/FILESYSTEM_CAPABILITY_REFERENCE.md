# Filesystem Capability Reference

This document serves as the canonical reference for all primitives in the Filesystem Capability Library (Experience 002). All capabilities described here adhere strictly to the **Capability Development Constitution** and rely on the shared infrastructure in `sys/file/shared/`.

---

## 1. Safe Execution Capabilities (Phase A)
These capabilities are non-mutating (or non-destructive) and execute without explicit physical confirmation.

### `sys.file.open`
- **Intents:** `open file`, `open directory`, `launch`, `start`
- **Parameters:** `target` (required)
- **Safety Level:** `normal`
- **Verification:** Target path exists prior to execution.
- **ACA Compatibility:** High. Can be seamlessly orchestrated by ACA.
- **Cloud Compatibility:** True. Completely stateless.
- **Presentation Policy:** `filesystem.open.success` (informative, no followup needed).
- **Example Composition:** `Search -> Open`

### `sys.file.copy`
- **Intents:** `copy`, `duplicate`, `clone`
- **Parameters:** `sources` (required), `destination_dir` (required), `collision_policy` (default: fail)
- **Safety Level:** `normal` (escalates to `dangerous` if collision policy is `overwrite`)
- **Verification:** Verification by identity (size/timestamps matches origin) at destination.
- **ACA Compatibility:** High.
- **Presentation Policy:** `filesystem.copy.success` (reassuring).
- **Example Composition:** `Search -> Copy -> Compress`

### `sys.file.move`
- **Intents:** `move`, `transfer`
- **Parameters:** `sources` (required), `destination_dir` (required), `collision_policy` (default: fail)
- **Safety Level:** `normal` (escalates to `dangerous` if overwrite)
- **Verification:** Same as `copy`, plus verifies origin paths are missing.
- **ACA Compatibility:** High.
- **Presentation Policy:** `filesystem.move.success`

### `sys.file.search`
- **Intents:** `find`, `search`, `locate`
- **Parameters:** `location` (required), `name_pattern`, `modified_after`, `modified_before`, `extensions`, `include_directories`, `min_size`, `max_size`, `sort_by`, `limit`
- **Safety Level:** `normal`
- **Verification:** Query verification (schema validation and result count).
- **Output:** Returns a `ResourceCollection` of heavily typed `FileResource` models.
- **ACA Compatibility:** Highest. Acts as the query backbone for all future pipelines.
- **Example Composition:** `Search -> Compress -> Recycle`

---

## 2. State Mutation Capabilities (Phase B)
These capabilities modify the filesystem. Destructive actions are strictly governed by Rules 16, 17, and 18 of the Constitution.

### `sys.file.create`
- **Intents:** `create folder`, `make directory`, `new file`, `touch`
- **Parameters:** `target` (required), `type` (file/directory), `collision_policy` (default: fail)
- **Safety Level:** `normal` (escalates if overwrite)
- **Verification:** Verifies existence and correct object type at target path.
- **Presentation Policy:** `filesystem.create.success`
- **Special Behavior:** Automatically builds all required parent directories recursively (user-friendly).

### `sys.file.rename`
- **Intents:** `rename`, `change name`
- **Parameters:** `source` (required), `new_name` (required), `collision_policy`
- **Safety Level:** `normal`
- **Verification:** Size and timestamp identity verification on the renamed object.
- **Special Behavior:** Explicitly rejects cross-directory attempts with `USE_MOVE_CAPABILITY`. Handles Windows case-only renames automatically.

### `sys.file.compress`
- **Intents:** `compress files`, `zip folder`, `create archive`
- **Parameters:** `sources` (required), `destination_dir` (required), `archive_name` (required), `format`, `collision_policy`
- **Safety Level:** `normal`
- **Verification:** Verifies archive existence, size > 0, binary readability (`testzip`), and total entry count.
- **Output:** Returns a `ResourceCollection` of the created archive.
- **Example Composition:** `Search -> Compress -> Recycle Originals`

---

## 3. Deletion Hierarchy

### `sys.file.recycle` (Default Delete)
- **Intents:** `delete`, `remove`, `delete files`
- **Parameters:** `targets` (required)
- **Safety Level:** `normal`
- **Verification:** Original paths are missing + Windows Shell API returned `0` (Success).
- **Presentation Policy:** `filesystem.recycle.success`. Contains `recovery_hint: true` and `tone: reassuring`.
- **Constitutional Guard:** Rule 17 (Recover Before Destroy). All general deletion requests route here natively.

### `sys.file.delete` (Permanent Delete)
- **Intents:** `delete permanently`, `delete forever`, `destroy`
- **Parameters:** `targets` (required)
- **Safety Level:** `dangerous` (requires physical user confirmation)
- **Verification:** Original paths are completely missing.
- **Presentation Policy:** `filesystem.delete.success`. Contains `recovery_hint: false` and `tone: serious`.
- **Constitutional Guard:** Rule 16 (Irreversible Destructive Actions). Will never execute without explicit physical UI confirmation.
