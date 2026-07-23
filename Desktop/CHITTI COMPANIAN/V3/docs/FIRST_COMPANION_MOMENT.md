# FIRST COMPANION MOMENT (CHITTI V1.1)

This document defines the complete end-to-end acceptance criteria for CHITTI's first production-quality feature: **Resume Activity**. 

It serves as the contract against which every implementation is validated.

---

## Goal
The user issues the command:
> **"Continue my React project."**

CHITTI restores the last coding session using verified OS execution and Activity Memory, providing a seamless "Companion Moment."

---

## Preconditions
- Node.js is installed and in the system PATH.
- VS Code (or the designated editor) is installed and in the system PATH.
- Chrome (or the default system browser) is available.
- The target Project is captured within `ActivityMemory`.
- An Activity record exists for the project.

---

## Execution Flow

1. **Load ActivityMemory**
2. **Resolve ProjectProfile** (Dynamically constructed, no hardcoded paths)
3. **Preflight** (Verify workspace path and required tools)
4. **Recovery** (If needed: Interactive prompts for missing `node_modules`, tools, etc.)
5. **Launch IDE** (Open the workspace in the editor)
6. **Launch Terminal** (Start the local dev server)
7. **Verify Server** (Poll until port is open, HTTP responds, and signatures match)
8. **Launch Browser** (Open the development URL)
9. **Presentation** (Display rich status and metrics on the Dashboard)
10. **Behavior Narration** (Emit semantic lifecycle events for the Behavior Engine)
11. **Capture Activity** (Record the new session)
12. **Metrics** (Record `ResumeMetrics` including restore time, verification time, etc.)

---

## Success Criteria
The V1.1 feature is considered complete and successful ONLY when all of the following are true:

- [ ] Workspace is restored successfully without manual intervention.
- [ ] Verification passed (Preflight and Deep Service Verification).
- [ ] Browser opened automatically to the correct URL after server readiness.
- [ ] Dashboard is updated with live progress and the final Presentation payload.
- [ ] Narration completed naturally, driven by semantic events (not raw TTS calls).
- [ ] `ResumeMetrics` are recorded and exposed for Developer Mode diagnostics.
- [ ] `ActivityMemory` is updated with the new session.
- [ ] **Zero Hardcoding**: No project-specific paths, commands, ports, or browser assumptions exist in the Orchestrator.
