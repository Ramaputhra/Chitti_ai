import time
from typing import Any, Dict

from desktop.platform.shared.interfaces.context_builder import IContextBuilder
from desktop.platform.shared.interfaces.conversation_manager import IConversationManager
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.state import IStateManager
from desktop.platform.shared.models.ai import ConversationContext


class ContextBuilder(IContextBuilder):
    def __init__(
        self,
        conversation_manager: IConversationManager,
        state_manager: IStateManager,
        logger: ILoggingService,
    ) -> None:
        self.conversation_manager = conversation_manager
        self.state_manager = state_manager
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "ContextBuilder"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {}

    def build_context(self) -> ConversationContext:
        # Mock memory, emotion, and capabilities for now
        desktop_state = {"os": "Windows", "active_window": "VS Code"}
        emotion = "Neutral"
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        memory = {}
        capabilities = ["Filesystem", "Browser", "System"]
        preferences = {"language": "English", "theme": "Dark"}

        session = self.conversation_manager.get_current_session()
        history = session.artifacts if session else []

        context = ConversationContext(
            desktop_state=desktop_state,
            conversation_history=history,
            emotion=emotion,
            time=current_time,
            memory=memory,
            capabilities=capabilities,
            preferences=preferences,
        )
        self.logger.info("Context built successfully")
        return context
