from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.ai import LLMResponse, Prompt, ToolInvocation
from desktop.platform.shared.models.safety import (
    PromptValidationResult,
    ResponseValidationResult,
    ToolValidationResult,
)


class IAISafetyLayer(IService):
    """
    Evaluates inputs and outputs across three distinct safety gates to prevent
    prompt injection, restricted capability execution, and malformed outputs.
    """
    def validate_prompt(self, prompt: Prompt) -> PromptValidationResult:
        ...

    def validate_response(self, response: LLMResponse) -> ResponseValidationResult:
        ...

    def validate_tool_invocation(self, invocation: ToolInvocation) -> ToolValidationResult:
        ...
