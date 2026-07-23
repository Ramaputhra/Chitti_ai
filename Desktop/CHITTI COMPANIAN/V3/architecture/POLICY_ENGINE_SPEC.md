# Policy Engine Specification

> **1. The architecture must remain deterministic by default. AI reasoning is an optional capability, never a mandatory dependency for system operation. Any feature that can be executed through deterministic logic must not require an LLM.**
>
> **2. Every runtime must be independently testable, restartable, and replaceable without requiring changes to unrelated runtimes.**
>
> **5. Every runtime, planner, scheduler, and capability must exist only to improve the AI Desktop Companion experience. Architectural complexity must always provide measurable product value.**

## 1. Purpose
Centralized security, authentication, and permission evaluation for protected desktop actions. It enforces user-configured security levels without managing direct UI interaction or speech recognition.

## 2. Responsibilities
- **Configurable Security Levels:** Support four explicit authentication modes:
  - `OFF`: No authentication required.
  - `PIN`: Protected actions require PIN input.
  - `VOICE`: Protected actions require successful `SpeakerVerified` events.
  - `VOICE + PIN`: Prioritize voice verification, fallback to PIN if failed.
- **Action Evaluation:** Intercept protected intents or workflows and either grant, deny, or suspend them pending authentication.
- **PIN Fallback Logic:** If an action requires authentication and voice fails (or is skipped), prompt the Application UI to display a secure dialog.
  - Timeout strictly after 30 seconds.
  - Upon timeout or cancellation, automatically close the dialog, drop the pending request, and return CHITTI to the system tray.

## 3. Interfaces
- **Subscribes to:** `SpeakerVerified`, `IntentRecognized` (or Workflow requests).
- **Emits:** `AuthenticationRequested` (to App UI), `PolicyEvaluated` (Action Approved/Denied).
- **API:** Implement `IRuntime`.

## 4. Events
- `PolicyEvaluated`
  ```yaml
  action_id: "open_browser"
  approved: true
  reason: "authenticated_via_voice"
  ```
- `AuthenticationRequested`
  ```yaml
  type: "PIN"
  timeout_seconds: 30
  ```

## 5. Dependencies
- EventBus
- User Settings (Security Mode configuration)

## 6. Failure Modes
- Default to **Deny-by-default lock** if policy rules are corrupted or unreadable.
- Abandon pending requests instantly if UI times out.

## 7. Lifecycle
Follows standard `IRuntime` strict state machine (`CREATED` -> `INITIALIZING` -> `READY` -> `RUNNING`).

## 8. Future Extensions
- Location-aware trust policies.
- Zero-trust model capabilities.

## 9. Out of Scope
- **Execution & UI:** The Policy Engine evaluates rules and requests auth but *never* executes capabilities or draws UI windows directly.
- **Voice Enrollment:** Enrollment logic belongs to the Speech Runtime/Auth provider.

## Acceptance Criteria

□ Purpose is defined
□ Responsibilities are complete
□ Interfaces are documented
□ Events are documented
□ Dependencies are identified
□ Failure modes are defined
□ Lifecycle is complete
□ Future extensions are identified
□ Out-of-scope boundaries are defined
□ Version 1 / Version 2 / Final Architecture comparison is complete
