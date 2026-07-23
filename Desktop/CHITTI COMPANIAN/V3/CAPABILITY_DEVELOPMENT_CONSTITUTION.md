# CHITTI: Capability Development Constitution

The core architecture (Experience 001 v1.0) is frozen. The following 15 requirements must be met by **every** capability added to the CHITTI platform to ensure horizontal scaling does not compromise architectural integrity.

## 1. Capability Manifest
Every capability must define a declarative YAML manifest (`manifest.yaml`) specifying its signature, domain (e.g. `sys.file.*`), parameters, failure policies, and metadata.
*Note: To ensure decoupling, manifest files must be separated per runtime (see below).*

## 2. Planner Integration (`planner.yaml`)
The capability must seamlessly translate from the Semantic Runtime's `DesktopIntent` via declarative Execution Steps inside the Planner. The planner owns `planner.yaml`.

## 3. Verification Manifest (`verification.yaml`)
The capability must leverage an "Evidence-First" verification model (e.g., verifying `os.path.exists` rather than relying on Vision inference unless absolutely necessary). The verification runtime owns `verification.yaml`.

## 4. Presentation Policy (`presentation.yaml`)
The capability must define deterministic success and failure states that map to clean `ResponseIntent` outputs, keeping personality completely decoupled from the capability execution. The presentation runtime owns `presentation.yaml`.

## 5. ACA Compatibility (Adaptive Capability Acquisition)
The capability's parameters must be generalizable. The `WorkflowGeneralizer` must be able to strip explicit constants out of the executed workflow to store it as a reusable template.

## 6. Local/Cloud Compatibility
The capability must remain entirely blind to the execution provider. It must be stateless and produce identical verified outcomes regardless of whether a local or cloud LLM processed the intent.

## 7. End-to-End Integration Test
Every capability requires an isolated capability runtime integration test asserting that its adapter executes and emits the proper status events.

## 8. Experience Test
Capabilities must pass a full pipeline simulation (Wake Word -> Intent -> Planner -> Execution -> Verification -> Presentation -> Follow-up). 
Every experience test must validate three scenarios:
1. **Happy Path**: Everything succeeds.
2. **Recoverable Failure**: Planner retries and eventually succeeds.
3. **Permanent Failure**: Graceful termination and proper user presentation.

## 9. Failure Policy
The capability must explicitly define in its manifest:
- Recoverable failures
- Non-recoverable failures
- User-facing failure messages
- Retry policy

No capability should invent its own error handling.

## 10. Security & Safety Policy
Every capability must declare its safety level in its manifest:
- `safety_level: safe` (e.g., `confirmation_required: false`)
- `safety_level: dangerous` (e.g., `confirmation_required: true`, `undo_supported: true`)

## 11. Performance Expectations
Every capability should define expected timing in its manifest:
- `fast`: <500ms
- `normal`: <5s
- `long_running`: true
The Presentation Runtime adapts based on this (e.g., fast = silent, long = working animation + ETA).

## 12. Capability Metadata
Every capability must expose metadata:
- `capability_id`: e.g. `sys.file.copy`
- `version`: e.g. `1.0`
- `author`: e.g. `core`
- `supports_learning`: e.g. `true`
- `supports_cloud`: e.g. `false`
- `platforms`: e.g. `[windows]`

Furthermore, a `compatibility` block should be included for future-proofing:
```yaml
compatibility:
    minimum_runtime: 1.0
    deprecated: false
    replaces: null
```

## 13. Capability Atomicity
Every capability must represent **one atomic action** (e.g., `sys.file.copy`, `sys.browser.open`).
Compound behaviors (e.g., `copy_and_zip`) belong in the Planner, Workflow Runtime, or ACA learned workflows, never inside a capability.

## 14. Capability Idempotency Declaration
Every manifest should declare whether repeated execution is safe (e.g., `idempotent: true` or `false`). This is valuable for retries, cloud execution, ACA, and failure recovery.

## 15. Capability Cost
Every capability should expose an estimated execution cost (e.g., cpu, memory, disk, network) so the planner can optimize workflows without changing the capability itself.

## 16. Irreversible Destructive Actions
CHITTI never performs irreversible destructive actions autonomously. CHITTI may plan, prepare, verify, and present destructive operations (e.g., permanent deletion, format), but the final irreversible action must always require an explicit physical user confirmation. Voice commands alone are never sufficient.

## 17. Recover Before Destroy
CHITTI always prefers recoverable actions over irreversible actions. Unless the user explicitly requests permanent deletion, all delete operations are redirected to the Windows Recycle Bin (or equivalent recoverable state).

## 18. Recovery Communication
Whenever CHITTI performs a recoverable action instead of a destructive one, it must clearly inform the user where and how the data can be recovered.

## 19. Least Intrusive Web Execution
Web tasks must execute using the simplest runtime capable of completing the task. The escalation path is strictly: Search → Crawl → Headless Browser → Interactive Browser.

## 20. Browser Visibility
Interactive browser windows must only be opened when user interaction or specific website state strictly requires it. Information retrieval must remain invisible.

## 21. User Privacy
Whenever authentication or sensitive information is required, CHITTI must announce it, the avatar must step aside, the browser remains open, and CHITTI must wait until the user calls it again. CHITTI never watches password entry.

## 22. Safe Browsing Policy
CHITTI must not intentionally navigate to, search for, automate, or interact with websites whose primary purpose is adult sexual content, pornography, illegal content, malware distribution, phishing, piracy, or other unsafe material. The Planner and Web Execution Policy Runtime must reject such requests before browser execution.

## 24. Web Capabilities Are Read-Oriented by Default
Unless explicitly requested by the user, Web Capabilities shall not create accounts, submit forms, purchase products, publish content, send messages, or modify remote state. Default mode is Observe, Extract, Verify, Present. Only explicit user intent allows mutation.

## 25. The Planner Produces Descriptions, Never Side Effects
The Planner's sole responsibility is generating immutable planning artifacts (`WorkflowPlan`). It must never invoke a runtime, access the filesystem or browser, execute capabilities, verify evidence, or perform any action with side effects.

## 26. Workflow Owns Orchestration
The Workflow Runtime is the only runtime permitted to orchestrate multi-step execution. Capabilities execute exactly one atomic action and remain unaware of preceding or subsequent workflow steps. No layer leaks into another.

## 27. Expression Never Alters Execution
Expression may communicate, delay, interrupt, or reorder presentation, but it shall never modify workflow execution, verification outcomes, or planner decisions.

## 28. Core Dependency Vendoring (In-lining)
To guarantee total offline autonomy, eliminate bloat, and prevent supply chain attacks, CHITTI shall prefer vendoring (in-lining) critical open-source execution logic over relying on package managers (e.g., pip) for core desktop and system interactions. External dependencies should only be used during prototyping; for production, only the essential, audited source code must be extracted and placed into `desktop/platform/native/`.

---
**Approval Rule**: No capability may be merged into the standard library unless it satisfies all 28 elements of this Constitution. Capability directories must mirror their hierarchical namespace (e.g., `sys/file/open/`).
