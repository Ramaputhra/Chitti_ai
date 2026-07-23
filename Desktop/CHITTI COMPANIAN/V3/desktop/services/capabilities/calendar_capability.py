import time
from typing import Any, Dict, List

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.calendar_provider import ICalendarProvider
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.artifact import CalendarArtifact
from desktop.platform.shared.models.capability import CapabilityDescriptor


class CalendarCapability(ICapability):
    """
    Provides calendar operations (query, create, move) abstracting away the specific ICalendarProvider.
    """
    def __init__(self, logger: ILoggingService, provider: ICalendarProvider) -> None:
        self.logger = logger
        self.providers = [provider]
        self._state = ServiceState.STOPPED
        self._cache = {}
        self._cache_ttl = 120.0

    @property
    def name(self) -> str:
        return "CalendarCapability"

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
            return self.query_calendar(parameters.get("query", ""))
        raise NotImplementedError(f"Action {action} not supported by {self.name}")

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name=self.name,
            description="Access and manage user calendar events.",
            actions=["query", "create", "move"],
        )

    def query_calendar(self, query: str) -> List[CalendarArtifact]:
        cache_key = f"query:{query}"
        now = time.time()
        
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if now - entry["time"] < self._cache_ttl:
                self.logger.info(f"CalendarCapability cache hit for query: {query}")
                return entry["data"]

        results = []
        for provider in self.providers:
            if provider.state == ServiceState.RUNNING:
                try:
                    results.extend(provider.query_calendar(query))
                except Exception as e:
                    self.logger.warning(f"{provider.name} failed to query calendar: {e}")
                    
        self._cache[cache_key] = {"time": now, "data": results}
        return results
