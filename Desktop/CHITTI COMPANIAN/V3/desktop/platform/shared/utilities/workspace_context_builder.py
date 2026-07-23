import concurrent.futures
from typing import Optional

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.models.workspace_context import WorkspaceContext
from desktop.services.capabilities.calendar_capability import CalendarCapability
from desktop.services.capabilities.mail_capability import MailCapability
from desktop.services.capabilities.desktop_context_capability import DesktopContextCapability
from desktop.services.capabilities.notes_capability import NotesCapability
from desktop.services.capabilities.documents_capability import DocumentsCapability


class WorkspaceContextBuilder:
    """
    Orchestrates the concurrent gathering of data from all capabilities
    to build a unified WorkspaceContext object.
    """
    @staticmethod
    def build(
        logger: ILoggingService,
        calendar_cap: Optional[CalendarCapability] = None,
        mail_cap: Optional[MailCapability] = None,
        context_cap: Optional[DesktopContextCapability] = None,
        notes_cap: Optional[NotesCapability] = None,
        docs_cap: Optional[DocumentsCapability] = None,
        meeting_query: str = ""
    ) -> WorkspaceContext:
        
        ctx = WorkspaceContext()

        def fetch_calendar():
            if not calendar_cap: return []
            try: return calendar_cap.execute("query", {"query": "today"})
            except Exception as e:
                logger.warning(f"Failed to fetch calendar: {e}")
                return []

        def fetch_mail():
            if not mail_cap: return []
            try: return mail_cap.execute("query", {"query": "is:unread"})
            except Exception as e:
                logger.warning(f"Failed to fetch mail: {e}")
                return []

        def fetch_desktop():
            if not context_cap: return []
            try: return [context_cap.execute("query", {})]
            except Exception as e:
                logger.warning(f"Failed to fetch desktop context: {e}")
                return []

        def fetch_notes():
            if not notes_cap or not meeting_query: return []
            try: return notes_cap.execute("query", {"query": meeting_query})
            except Exception as e:
                logger.warning(f"Failed to fetch notes: {e}")
                return []

        def fetch_docs():
            if not docs_cap: return []
            try: return docs_cap.execute("recent", {})
            except Exception as e:
                logger.warning(f"Failed to fetch documents: {e}")
                return []

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_calendar = executor.submit(fetch_calendar)
            future_mail = executor.submit(fetch_mail)
            future_desktop = executor.submit(fetch_desktop)
            future_notes = executor.submit(fetch_notes)
            future_docs = executor.submit(fetch_docs)

            ctx.calendar_events = future_calendar.result()
            ctx.unread_emails = future_mail.result()
            
            desktop_arts = future_desktop.result()
            ctx.desktop_state = [a for a in desktop_arts if a]
            
            ctx.meeting_notes = future_notes.result()
            ctx.recent_documents = future_docs.result()

        return ctx
