# CHITTI V1 MASTER ENGINEERING SPECIFICATION

## Part 3 --- Runtime Specifications

**Version:** 1.0 Draft

# Runtime Contract

Every runtime SHALL define: - Purpose - Inputs - Outputs - Published
Events - Consumed Events - Dependencies - Failure Modes

------------------------------------------------------------------------

# ConversationRuntime

Purpose: Own conversational state.

Responsibilities: - Session lifecycle - Entity resolution - Context
routing - InteractionEnvelope consumption

Must NOT: - Execute capabilities - Persist data directly - Build
execution workflows

------------------------------------------------------------------------

# AIRuntime

Purpose: Semantic reasoning.

Responsibilities: - Prompt assembly - Intent resolution - Response
generation

Must NOT: - Execute desktop actions - Verify outcomes

------------------------------------------------------------------------

# InferenceRuntime

Purpose: Abstract inference providers.

Responsibilities: - Provider selection - Streaming - Health - Model
lifecycle

Supports: - GGUF - Future cloud providers

------------------------------------------------------------------------

# PlannerRuntime

Purpose: Convert validated intents into deterministic plans.

Must remain capability-agnostic.

Outputs: WorkflowRequest.

------------------------------------------------------------------------

# WorkflowRuntime

Purpose: Own workflow state machine.

Responsibilities: - Sequencing - Retry policy - Cancellation - Progress

------------------------------------------------------------------------

# ExecutionRuntime

Purpose: Execute capabilities.

Responsibilities: - Capability lookup - Invocation - Result publication

Must NOT verify execution.

------------------------------------------------------------------------

# VerificationRuntime

Purpose: Confirm factual outcomes.

Sources: - Win32 - Browser - OCR - Activity - Filesystem

Only VerificationRuntime may declare execution success.

------------------------------------------------------------------------

# BehaviorRuntime

Purpose: Determine companion behavior after verified outcomes.

------------------------------------------------------------------------

# ExpressionRuntime

Purpose: Render behavior into text, voice, or UI.

------------------------------------------------------------------------

# MemoryRuntime

Purpose: Persist: - Conversation history - Episodes - Activities -
Pinned facts

ConversationSession remains runtime-only.

------------------------------------------------------------------------

# PackageManagerRuntime

Purpose: Discover packages and register capabilities dynamically.

Manual registration is transitional only.

------------------------------------------------------------------------

# Engineering Rules

Every runtime shall have: - one owner - one responsibility - clear
boundaries - no duplicated authority

*End of Part 3.*
