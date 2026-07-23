import time
from typing import Any, Dict, List

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.mail_provider import IMailProvider
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.artifact import EmailArtifact
from desktop.platform.shared.models.capability import CapabilityDescriptor


class MailCapability(ICapability):
    """
    Provides mail operations (read, reply, archive) abstracting away the specific IMailProvider.
    """
    def __init__(self, logger: ILoggingService, provider: IMailProvider) -> None:
        self.logger = logger
        # In a real setup, we might pick the primary provider, or iterate over all
        self.providers = [provider]
        self._state = ServiceState.STOPPED
        self._cache = {}
        self._cache_ttl = 120.0

    @property
    def name(self) -> str:
        return "MailCapability"

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
        return {
            "active_providers": [p.name for p in self.providers if p.state == ServiceState.RUNNING]
        }

    def execute(self, action: str, parameters: Dict[str, Any]) -> Any:
        if action == "query":
            return self.query_mail(parameters.get("query", ""))
        raise NotImplementedError(f"Action {action} not supported by {self.name}")

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name=self.name,
            description="Access and manage user email.",
            actions=["query", "reply", "archive"],
        )

    def query_mail(self, query: str) -> List[EmailArtifact]:
        cache_key = f"query:{query}"
        now = time.time()
        
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if now - entry["time"] < self._cache_ttl:
                self.logger.info(f"MailCapability cache hit for query: {query}")
                return entry["data"]

        results = []
        for provider in self.providers:
            if provider.state == ServiceState.RUNNING:
                try:
                    results.extend(provider.query_mail(query))
                except Exception as e:
                    self.logger.warning(f"{provider.name} failed to query mail: {e}")
                    
        self._cache[cache_key] = {"time": now, "data": results}
        return results
