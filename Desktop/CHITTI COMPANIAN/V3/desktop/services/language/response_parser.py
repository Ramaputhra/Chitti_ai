import json
import uuid
from typing import Any, Dict

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.response_parser import IResponseParser
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import LLMResponse, ToolInvocation


class ResponseParser(IResponseParser):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "ResponseParser"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> Dict[str, Any]:
        return {}

    def _extract_json_block(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def parse_response(self, raw_text: str) -> LLMResponse:
        self.logger.info("Parsing LLM response")
        text = self._extract_json_block(raw_text)

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {e}")
            # Return a graceful fallback LLMResponse rather than crashing
            return LLMResponse(
                text="I'm sorry, my cognitive layer produced an invalid response.",
                raw_json=raw_text,
                finish_reason="parser_error"
            )

        # Validate Schema Version
        schema_version = data.get("version", 1)
        response_text = data.get("response", "")
        
        tool_invocations = []
        if "tool" in data and isinstance(data["tool"], dict):
            t_data = data["tool"]
            tool_name = t_data.get("name", "UnknownTool")
            args = t_data.get("arguments", {})
            
            tool_invocations.append(
                ToolInvocation(
                    id=str(uuid.uuid4()),
                    tool_name=tool_name,
                    arguments=args,
                    confidence=1.0,
                    source="LLM"
                )
            )

        return LLMResponse(
            text=response_text,
            tool_invocations=tool_invocations,
            raw_json=text,
            schema_version=schema_version
        )
