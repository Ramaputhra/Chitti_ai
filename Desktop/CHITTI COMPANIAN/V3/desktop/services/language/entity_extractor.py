from typing import Any, Dict

from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.entity import PersonEntity, TimeEntity, LocationEntity


class EntityExtractionRuntime:
    """
    Subscribes to LANGUAGE_TEXT_RECOGNIZED.
    Extracts canonical entities from raw multilingual text.
    Emits ENTITY_EXTRACTION_COMPLETED.
    """
    def __init__(self, event_bus: IEventBus, logger: ILoggingService) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "EntityExtractionRuntime"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self.event_bus.subscribe(
            SystemEvents.LANGUAGE_TEXT_RECOGNIZED, self._process_text
        )
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {}

    def _process_text(self, event: Event) -> None:
        text = event.payload.get("text", "")
        language = event.payload.get("language", "en")
        confidence = event.payload.get("confidence", 1.0)
        source = event.payload.get("source", "audio")

        if not text:
            return

        # Milestone 1: Lightweight Mock/Regex Extraction
        entities = self._extract_entities(text, language)

        self.logger.info(f"Extracted Entities: {len(entities)} from text")
        
        self.event_bus.publish(
            Event(
                SystemEvents.ENTITY_EXTRACTION_COMPLETED,
                self.name,
                {
                    "text": text,
                    "language": language,
                    "confidence": confidence,
                    "source": source,
                    "entities": entities
                },
            )
        )

    def _extract_entities(self, text: str, language: str) -> Dict[str, Any]:
        entities = {}
        
        lower_text = text.lower()
        
        # Mock extraction for demonstration
        if "రాముకి" in lower_text or "ramu" in lower_text:
            entities["recipient"] = PersonEntity(
                original_text="రాముకి" if "రాముకి" in lower_text else "ramu",
                confidence=0.9,
                display_name="రాము" if "రాముకి" in lower_text else "Ramu",
                contact_id="contact_123"
            )
            
        if "రేపు ఉదయం 10 గంటలకు" in lower_text or "tomorrow morning at 10" in lower_text:
            entities["time"] = TimeEntity(
                original_text="రేపు ఉదయం 10 గంటలకు" if "రేపు" in lower_text else "tomorrow morning at 10",
                confidence=0.85,
                timestamp="2026-07-14T10:00:00+05:30",
                timezone="Asia/Kolkata"
            )

        return entities
