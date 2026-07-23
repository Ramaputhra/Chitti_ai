from typing import List
from desktop.models.observation import Observation
from desktop.platform.observation.sources import (
    ProcessSource, WindowSource, DesktopSource, ClipboardSource, FilesystemSource
)

class ObservationManager:
    """
    Coordinates access to isolated, read-only observation sources.
    Consumers (like VerificationRuntime) depend ONLY on this manager.
    """
    def __init__(self):
        self.process_source = ProcessSource()
        self.window_source = WindowSource()
        self.desktop_source = DesktopSource()
        self.clipboard_source = ClipboardSource()
        self.filesystem_source = FilesystemSource()

    def observe_process(self, correlation_id: str, session_id: str, pid: int = None, name: str = None) -> List[Observation]:
        return self.process_source.observe_process(correlation_id, session_id, pid, name)

    def observe_windows(self, correlation_id: str, session_id: str, pid: int = None) -> List[Observation]:
        return self.window_source.observe_windows(correlation_id, session_id, pid)

    def observe_desktop(self, correlation_id: str, session_id: str) -> Observation:
        return self.desktop_source.observe_desktop(correlation_id, session_id)

    def observe_clipboard(self, correlation_id: str, session_id: str) -> Observation:
        return self.clipboard_source.observe_clipboard(correlation_id, session_id)

    def observe_file(self, correlation_id: str, session_id: str, filepath: str) -> Observation:
        return self.filesystem_source.observe_file(correlation_id, session_id, filepath)
