from typing import List, Dict, Any, Type
from desktop.models.conversation import ConversationSession

class ContextProvider:
    """Base class for all context providers."""
    def provide_context(self, session: ConversationSession, intent: str) -> List[Dict[str, str]]:
        return []

class ConversationContextProvider(ContextProvider):
    def provide_context(self, session: ConversationSession, intent: str) -> List[Dict[str, str]]:
        messages = []
        if session.companion_context:
            messages.append({"role": "system", "content": f"Companion Mode: {session.companion_context.mode}"})
        
        # Add recent history
        history_window = session.history[-20:] if len(session.history) > 20 else session.history
        for msg in history_window:
            messages.append({"role": msg["role"], "content": msg["content"]})
        return messages

class ExecutionContextProvider(ContextProvider):
    def provide_context(self, session: ConversationSession, intent: str) -> List[Dict[str, str]]:
        # Only inject if state query or action intent
        if intent in ["StateQueryIntent", "QuestionIntent"] and session.execution_context.last_success:
            return [{"role": "system", "content": f"Execution Context:\nLast Success: {session.execution_context.last_success}"}]
        return []

class WorkspaceContextProvider(ContextProvider):
    def provide_context(self, session: ConversationSession, intent: str) -> List[Dict[str, str]]:
        if intent in ["QuestionIntent", "ReasoningIntent", "WritingIntent"] and session.companion_context.project:
            return [{"role": "system", "content": f"Active Project: {session.companion_context.project}"}]
        return []

class ActivityContextProvider(ContextProvider):
    def provide_context(self, session: ConversationSession, intent: str) -> List[Dict[str, str]]:
        # Fetch the latest activity snapshot if available
        # In this implementation, memory_runtime keeps it or we query it. 
        # But wait, session has no direct memory_runtime access. We can just use sqlite directly like MemoryRuntime does,
        # or we assume we can fetch it. Let's just do a direct sqlite fetch to avoid circular dependency.
        import sqlite3
        try:
            with sqlite3.connect("data/chitti_memory.db") as conn:
                cursor = conn.execute("SELECT application, project_name, workspace_path FROM activity_history ORDER BY timestamp DESC LIMIT 1")
                row = cursor.fetchone()
                if row:
                    app, proj, path = row
                    return [{"role": "system", "content": f"User's Current Activity:\nApplication: {app}\nProject: {proj}\nWorkspace: {path}"}]
        except Exception:
            pass
        return []

class EntityContextProvider(ContextProvider):
    def provide_context(self, session: ConversationSession, intent: str) -> List[Dict[str, str]]:
        if session.recent_entities:
            entities_str = ", ".join([e.display for e in session.recent_entities])
            return [{"role": "system", "content": f"Recent Entities: {entities_str}"}]
        return []

class CapabilityContextProvider(ContextProvider):
    def provide_context(self, session: ConversationSession, intent: str) -> List[Dict[str, str]]:
        if intent in ["QuestionIntent", "CommandIntent", "SmallTalkIntent"]:
            # Provide grounding on what CHITTI can do
            capabilities = "Launch applications, execute terminal commands, manage browser, open files, resume activities."
            return [{"role": "system", "content": f"Installed Capabilities: {capabilities}"}]
        return []

class ContextAssembler:
    def __init__(self):
        self.providers: List[ContextProvider] = [
            ConversationContextProvider(),
            ExecutionContextProvider(),
            WorkspaceContextProvider(),
            EntityContextProvider(),
            CapabilityContextProvider(),
            ActivityContextProvider()
        ]
        
    def assemble_prompt(self, session: ConversationSession, intent: str, system_prompt: str) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": system_prompt}]
        
        for provider in self.providers:
            messages.extend(provider.provide_context(session, intent))
            
        return messages
