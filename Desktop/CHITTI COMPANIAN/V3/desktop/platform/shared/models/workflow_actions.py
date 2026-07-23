"""
Universal Workflow Action Primitives.
The WorkflowExecutor interprets these—never the Planner.
"""


class WorkflowAction:
    """Universal, implementation-agnostic action primitives for the Executor."""
    INVOKE_CAPABILITY = "InvokeCapability"     # Route to a registered capability (Skill / Tool / API)
    RETRIEVE_MEMORY = "RetrieveMemory"         # Fetch from memory runtime
    STORE_MEMORY = "StoreMemory"               # Persist to memory runtime
    REASON = "Reason"                           # Delegate to LLM/reasoning runtime
    SPEAK = "Speak"                             # Emit text through TTS pipeline
    ANIMATE = "Animate"                         # Emit expression/animation event
    WAIT = "Wait"                               # Pause execution for duration_ms
    ASK_QUESTION = "AskQuestion"               # Emit a clarification question via TTS then await response
    EXECUTE_SYSTEM_ACTION = "ExecuteSystemAction"  # OS-level or device action
