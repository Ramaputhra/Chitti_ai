from typing import Any, Dict, List
from desktop.platform.shared.models.artifact import Artifact
from desktop.platform.shared.models.workspace_context import WorkspaceContext

class PromptComposer:
    """
    Utility to build structured prompts for the AI Orchestrator.
    Prevents workflows from concatenating strings randomly.
    """
    @staticmethod
    def compose_morning_brief(ctx: WorkspaceContext) -> str:
        context_lines = []
        for a in ctx.calendar_events:
            start = a.metadata.get("start_time", "Unknown")
            context_lines.append(f"- [Calendar] {start}: {a.content}")
        
        for a in ctx.unread_emails:
            sender = a.metadata.get("sender", "Unknown")
            subj = a.metadata.get("subject", "No Subject")
            context_lines.append(f"- [Email Unread] From {sender}: {subj}")
            
        for a in ctx.desktop_state:
            context_lines.append(f"- [System] {a.content}")

        context_payload = "\n".join(context_lines)
        if not context_payload:
            context_payload = "No context available. Only local data could be accessed."

        return (
            "You are CHITTI, a helpful assistant. Provide a short, natural Morning Brief for Rama based on the following context.\n"
            "If some data is missing, degrade gracefully (e.g., 'Your local calendar isn't connected yet.').\n"
            "Keep it conversational and brief.\n\n"
            f"Context Data:\n{context_payload}"
        )

    @staticmethod
    def compose_meeting_brief(ctx: WorkspaceContext) -> str:
        context_lines = []
        for a in ctx.calendar_events:
            start = a.metadata.get("start_time", "Unknown")
            context_lines.append(f"- [Calendar] {start}: {a.content}")
            
        for a in ctx.meeting_notes:
            title = a.metadata.get("title", "Unknown")
            context_lines.append(f"- [Notes] {title}: {a.content[:300]}...") # Snippet
            
        for a in ctx.recent_documents:
            title = a.metadata.get("title", "Unknown")
            context_lines.append(f"- [Recent Document] {title}: {a.content}")

        context_payload = "\n".join(context_lines)
        if not context_payload:
            context_payload = "No specific meeting context could be found."

        return (
            "You are CHITTI. Provide a proactive meeting brief based on the context data below.\n"
            "Synthesize the calendar events with any found notes or recent documents.\n"
            "Keep it professional and concise.\n\n"
            f"Context Data:\n{context_payload}"
        )

    @staticmethod
    def compose_email_summary(artifacts: List[Artifact]) -> str:
        emails = [a for a in artifacts if a.type == "EmailArtifact"]
        if not emails:
            return "No emails to summarize."
            
        context = []
        for e in emails:
            sender = e.metadata.get("sender", "Unknown")
            subj = e.metadata.get("subject", "No Subject")
            context.append(f"From: {sender}\nSubject: {subj}\nPreview: {e.content}\n---")
            
        payload = "\n".join(context)
        return (
            "You are CHITTI. Summarize the following bundle of unread emails naturally.\n"
            "Do not list them one by one unless there are only 1-2. Instead, group them conceptually "
            "(e.g., 'You have 3 newsletters and one invoice due tomorrow.').\n"
            "End by asking if the user wants to draft replies or archive any of them.\n\n"
            f"Emails:\n{payload}"
        )
