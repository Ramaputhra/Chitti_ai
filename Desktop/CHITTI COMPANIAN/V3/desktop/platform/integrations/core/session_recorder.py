import dataclasses
import json
import os
from datetime import datetime
from typing import Any, Dict

from desktop.platform.shared.interfaces.event_bus import IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.session_recorder import ISessionRecorder
from desktop.platform.shared.models.session import ConversationSession


class SessionRecorder(ISessionRecorder):
    def __init__(
        self,
        event_bus: IEventBus,
        logger: ILoggingService,
    ) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self.storage_dir = "sessions"
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "SessionRecorder"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        os.makedirs(self.storage_dir, exist_ok=True)
        self.logger.info(f"{self.name} initialized at {self.storage_dir}")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {}

    def save_session(self, session: ConversationSession) -> str:
        now = datetime.now()
        year_month = now.strftime("%Y/%m")
        path = os.path.join(self.storage_dir, year_month)
        os.makedirs(path, exist_ok=True)

        filename = f"session-{session.session_id}.json"
        filepath = os.path.join(path, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                data = dataclasses.asdict(session)
                data["state"] = session.state.name
                json.dump(data, f, indent=2)
            self.logger.info(f"Session saved to {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to save session: {e}")
            return ""
