from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.ai import LLMResponse


class IResponseParser(IService):
    """
    Acts as a secure firewall between raw LLM output and internal planning logic.
    Validates JSON schemas, attempts auto-repairs, and returns deterministic LLMResponse objects.
    """
    def parse_response(self, raw_text: str) -> LLMResponse:
        ...
