from typing import List

from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.skill import ISkill
from desktop.platform.shared.models.intent import Intent


class GreetingSkill(ISkill):
    def __init__(self, event_bus: IEventBus) -> None:
        self.event_bus = event_bus

    def id(self) -> str:
        return "core.greeting"

    def name(self) -> str:
        return "Greeting Skill"

    def version(self) -> str:
        return "1.0.0"

    def supported_intents(self) -> List[str]:
        return ["Greeting"]

    def execute(self, intent: Intent) -> None:
        self.event_bus.publish(
            Event(
                "WorkflowStep.GenerateResponse",
                "GreetingSkill",
                {"parameters": {"template": "Greeting"}},
            )
        )

    def health_check(self) -> bool:
        return True


class IdentitySkill(ISkill):
    def __init__(self, event_bus: IEventBus) -> None:
        self.event_bus = event_bus

    def id(self) -> str:
        return "core.identity"

    def name(self) -> str:
        return "Identity Skill"

    def version(self) -> str:
        return "1.0.0"

    def supported_intents(self) -> List[str]:
        return ["Identity"]

    def execute(self, intent: Intent) -> None:
        self.event_bus.publish(
            Event(
                "WorkflowStep.GenerateResponse",
                "IdentitySkill",
                {"parameters": {"template": "Identity"}},
            )
        )

    def health_check(self) -> bool:
        return True


class GratitudeSkill(ISkill):
    def __init__(self, event_bus: IEventBus) -> None:
        self.event_bus = event_bus

    def id(self) -> str:
        return "core.gratitude"

    def name(self) -> str:
        return "Gratitude Skill"

    def version(self) -> str:
        return "1.0.0"

    def supported_intents(self) -> List[str]:
        return ["Gratitude"]

    def execute(self, intent: Intent) -> None:
        self.event_bus.publish(
            Event(
                "WorkflowStep.GenerateResponse",
                "GratitudeSkill",
                {"parameters": {"template": "Gratitude"}},
            )
        )

    def health_check(self) -> bool:
        return True


class FarewellSkill(ISkill):
    def __init__(self, event_bus: IEventBus) -> None:
        self.event_bus = event_bus

    def id(self) -> str:
        return "core.farewell"

    def name(self) -> str:
        return "Farewell Skill"

    def version(self) -> str:
        return "1.0.0"

    def supported_intents(self) -> List[str]:
        return ["Farewell"]

    def execute(self, intent: Intent) -> None:
        self.event_bus.publish(
            Event(
                "WorkflowStep.GenerateResponse",
                "FarewellSkill",
                {"parameters": {"template": "Farewell"}},
            )
        )

    def health_check(self) -> bool:
        return True


class UnknownSkill(ISkill):
    def __init__(self, event_bus: IEventBus) -> None:
        self.event_bus = event_bus

    def id(self) -> str:
        return "core.unknown"

    def name(self) -> str:
        return "Unknown Skill"

    def version(self) -> str:
        return "1.0.0"

    def supported_intents(self) -> List[str]:
        return ["Unknown"]

    def execute(self, intent: Intent) -> None:
        self.event_bus.publish(
            Event(
                "WorkflowStep.GenerateResponse",
                "UnknownSkill",
                {"parameters": {"template": "Unknown"}},
            )
        )

    def health_check(self) -> bool:
        return True
