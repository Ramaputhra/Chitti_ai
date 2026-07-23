from desktop.platform.shared.interfaces.event_bus import Event

class InferenceRequested(Event):
    def __init__(self, text: str, session_id: str):
        super().__init__("InferenceRequested", "InferenceRuntime", {"text": text, "session_id": session_id})

class InferenceStarted(Event):
    def __init__(self, session_id: str):
        super().__init__("InferenceStarted", "InferenceRuntime", {"session_id": session_id})

class InferenceChunk(Event):
    def __init__(self, chunk: str, session_id: str):
        super().__init__("InferenceChunk", "InferenceRuntime", {"chunk": chunk, "session_id": session_id})

class InferenceCompleted(Event):
    def __init__(self, response: str, session_id: str):
        super().__init__("InferenceCompleted", "InferenceRuntime", {"response": response, "session_id": session_id})

class InferenceCancelled(Event):
    def __init__(self, session_id: str, reason: str = "User interrupted"):
        super().__init__("InferenceCancelled", "InferenceRuntime", {"session_id": session_id, "reason": reason})

class ToolCallProposed(Event):
    def __init__(self, tool: str, arguments: dict, session_id: str):
        super().__init__("ToolCallProposed", "InferenceRuntime", {"tool": tool, "arguments": arguments, "session_id": session_id})

class ConversationResponseGenerated(Event):
    def __init__(self, text: str, session_id: str):
        super().__init__("ConversationResponseGenerated", "InferenceRuntime", {"text": text, "session_id": session_id})
