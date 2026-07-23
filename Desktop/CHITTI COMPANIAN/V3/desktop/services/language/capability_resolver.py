"""
CapabilityResolver — the Planner's gateway to all execution capabilities.

The Planner never knows whether an intent is handled by a built-in Skill,
a remote API, a future Tool plugin, or an LLM. It simply asks the resolver:
  "Can you handle this intent?"

The resolver checks registered backends in priority order:
  1. SkillRegistry (local, deterministic, fast)
  2. (Future) ToolRegistry
  3. (Future) RemoteAPIRegistry

If nothing can handle the intent, it returns can_handle=False, and the
DecisionEngine will decide whether to fall back to LLM reasoning.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.skill import ISkill, ISkillRegistry


@dataclass
class CapabilityDescriptor:
    """
    Metadata about a capability to help the DecisionEngine route effectively.
    """
    can_handle: bool
    id: Optional[str] = None
    type: str = "none"           # "skill", "tool", "api"
    skill: Optional[ISkill] = None
    supports_streaming: bool = False
    requires_network: bool = False
    estimated_latency_ms: int = 50
    priority: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)


class CapabilityResolver:
    """
    Concrete implementation of the Capability Resolver.
    Registered with the DI container and injected into the DecisionEngine.
    The ActionPlanner never touches this directly — it goes through DecisionEngine.
    """

    def __init__(self, skill_registry: ISkillRegistry, logger: ILoggingService) -> None:
        self._skill_registry = skill_registry
        self._logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "CapabilityResolver"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self._logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self._logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {"state": self._state.value}

    def resolve(self, intent_type: str) -> CapabilityDescriptor:
        """
        Try to resolve a handler for the given intent type.
        Checks all registered backends in priority order.
        """
        # 1. Check local SkillRegistry
        skill = self._skill_registry.get_skill_for_intent(intent_type)
        if skill:
            self._logger.info(
                f"CapabilityResolver: intent '{intent_type}' resolved to Skill '{skill.name()}'"
            )
            return CapabilityDescriptor(
                can_handle=True,
                id=skill.id() if hasattr(skill, "id") else skill.name(),
                type="skill",
                skill=skill,
                requires_network=False,  # Core skills are offline
                estimated_latency_ms=20,
            )

        # 2. Future: check ToolRegistry, RemoteAPIRegistry, etc.

        self._logger.info(
            f"CapabilityResolver: no capability found for intent '{intent_type}'"
        )
        return CapabilityDescriptor(can_handle=False)
