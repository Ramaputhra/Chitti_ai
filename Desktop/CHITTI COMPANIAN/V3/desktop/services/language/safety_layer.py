from typing import Any, Dict

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.safety_layer import IAISafetyLayer
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import LLMResponse, Prompt, ToolInvocation
from desktop.platform.shared.models.safety import (
    PromptValidationResult,
    ResponseValidationResult,
    ToolValidationResult,
    ValidationStatus,
)


class AISafetyLayer(IAISafetyLayer):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "AISafetyLayer"

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

    def validate_prompt(self, prompt: Prompt) -> PromptValidationResult:
        self.logger.info("Validating Prompt")
        # Basic mock check
        if "ignore all previous instructions" in prompt.user_message.lower():
            return PromptValidationResult(ValidationStatus.REJECTED, "Prompt injection detected")
        return PromptValidationResult(ValidationStatus.PASSED)

    def validate_response(self, response: LLMResponse) -> ResponseValidationResult:
        self.logger.info("Validating Response")
        return ResponseValidationResult(ValidationStatus.PASSED)

    def validate_tool_invocation(self, invocation: ToolInvocation) -> ToolValidationResult:
        self.logger.info(f"Validating Tool Invocation: {invocation.tool_name}")
        # Could check if the tool exists or user has permissions
        return ToolValidationResult(ValidationStatus.PASSED)
