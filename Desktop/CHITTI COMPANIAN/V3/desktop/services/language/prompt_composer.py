from typing import Any, Dict

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.prompt_composer import IPromptComposer
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ConversationContext, Prompt


class PromptComposer(IPromptComposer):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "PromptComposer"

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

    def _build_system(self) -> str:
        return "You are CHITTI, an advanced AI desktop companion and future embodied robot."

    def _build_developer(self) -> str:
        return (
            "You are operating within the CHITTI Intelligence Runtime. "
            "You must output JSON intent structures when requesting tools. "
            "You cannot execute tools directly; the Tool Manager will execute them on your behalf."
        )

    def _build_safety(self) -> str:
        return "Do not execute destructive commands without user confirmation. Respect user privacy."

    def _build_memory(self, context: ConversationContext) -> str:
        if not context.memory:
            return ""
        return f"Memory Context:\n{context.memory}"

    def _build_desktop(self, context: ConversationContext) -> str:
        state_str = "\n".join(f"- {k}: {v}" for k, v in context.desktop_state.items())
        return f"Desktop State:\nTime: {context.time}\nEmotion: {context.emotion}\n{state_str}"

    def _build_tools(self, context: ConversationContext) -> str:
        caps_str = ", ".join(context.capabilities)
        return f"Available Capabilities:\n{caps_str}\n(Tool descriptors will be injected here dynamically)"

    def _build_conversation(self, context: ConversationContext) -> str:
        if not context.conversation_history:
            return ""
        lines = []
        for h in context.conversation_history[-5:]:  # Keep last 5 for context limits
            # Fallback formatting depending on artifact structure
            lines.append(f"Past Interaction: {h}")
        return "Conversation History:\n" + "\n".join(lines)

    def compose(self, context: ConversationContext, user_message: str) -> Prompt:
        self.logger.info("Composing Prompt...")
        prompt = Prompt(
            system_prompt=self._build_system(),
            developer_prompt=self._build_developer(),
            safety_prompt=self._build_safety(),
            memory_context=self._build_memory(context),
            desktop_context=self._build_desktop(context),
            tool_descriptions=self._build_tools(context),
            conversation=self._build_conversation(context),
            user_message=f"User: {user_message}",
        )
        return prompt
