import json
from typing import Any, Dict

from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.context import IContextEngine
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.intent import IIntentEngine
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.intent import Intent
from desktop.runtimes.inference.router import InferenceRouter
from desktop.platform.shared.models.ai import LLMRequest, Requirements

class IntentEngine(IIntentEngine):
    def __init__(
        self,
        event_bus: IEventBus,
        logger: ILoggingService,
        context_engine: IContextEngine,
        inference_router: InferenceRouter
    ) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self.context_engine = context_engine
        self.inference_router = inference_router
        self._state = ServiceState.STOPPED

        # Stage 1: Deterministic Dictionary
        self.dictionary = {
            "ఇమెయిల్": "EmailIntent",
            "email": "EmailIntent",
            "emails": "EmailIntent",
            "meeting": "MeetingIntent",
            "మీటింగ్": "MeetingIntent",
            "namaskaram": "Greeting",
            "hello": "Greeting",
            "hi": "Greeting",
            "bye": "Farewell",
            "goodbye": "Farewell",
            "thank you": "Gratitude",
            "thanks": "Gratitude",
            "workspace": "WorkspaceIntent",
            "profile": "WorkspaceIntent"
        }

    @property
    def name(self) -> str:
        return "IntentEngine"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self.event_bus.subscribe(
            SystemEvents.OBSERVATIONS_RESOLVED, self._process_observations
        )
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {}

    def _process_observations(self, event: Event) -> None:
        if event.payload.get("source") != "speech":
            return
            
        text = event.payload.get("text", "")
        language = event.payload.get("language", "en")
        confidence_score = event.payload.get("confidence", 1.0)
        entities = event.payload.get("entities", {})

        if not text or "noise" in text:
            self._ignore("Empty or noise")
            return

        # Stage 1: Dictionary Match
        intent_type, confidence = self._dictionary_match(text)
        
        # Stage 2: Pattern Match (skipped if dictionary had high confidence)
        if confidence < 0.90:
            pattern_intent, pattern_conf = self._pattern_match(text)
            if pattern_conf > confidence:
                intent_type = pattern_intent
                confidence = pattern_conf

        # Stage 3: LLM Fallback
        if confidence < 0.60:
            intent_type, confidence = self._llm_fallback(text, language)

        intent = Intent(type=intent_type, confidence=confidence)
        
        if intent.type == "Ignore" or intent.type == "Unknown":
            self._ignore(f"Low confidence or unknown intent: {intent.type}")
        else:
            self.logger.info(f"Detected Intent: {intent.type} ({intent.confidence}) [Lang: {language}]")
            self.event_bus.publish(
                Event(
                    SystemEvents.INTENT_DETECTED,
                    self.name,
                    {
                        "intent": intent, 
                        "original_text": text,
                        "language": language,
                        "confidence": confidence,
                        "parameters": entities # Canonical entities passed along
                    },
                )
            )

    def _dictionary_match(self, text: str) -> tuple[str, float]:
        tokens = text.split()
        for token in tokens:
            if token in self.dictionary:
                return self.dictionary[token], 0.95
        return "Unknown", 0.0

    def _pattern_match(self, text: str) -> tuple[str, float]:
        if "check my mail" in text or "read emails" in text or "ఇమెయిల్స్ చదవు" in text:
            return "EmailIntent", 0.95
        if "prep for" in text or "రాజుతో మీటింగ్" in text:
            return "MeetingIntent", 0.95
        return "Unknown", 0.0

    def _llm_fallback(self, text: str, language: str) -> tuple[str, float]:
        self.logger.info("Confidence < 0.60, triggering LLM fallback...")
        reqs = Requirements(needs_vision=False, fast=True)
        try:
            provider, model = self.inference_router.route(reqs)
            
            system_prompt = (
                "You are an intent classification engine. The user input might be in English, Telugu, or a mixture. "
                "Classify the intent into one of: Greeting, Farewell, Gratitude, EmailIntent, MeetingIntent, WorkspaceIntent, or Unknown. "
                "Respond ONLY with a JSON object: {\"intent\": \"<intent_name>\", \"confidence\": <float 0.0-1.0>}"
            )
            
            req = LLMRequest(
                system_prompt=system_prompt,
                messages=[{"role": "user", "content": text}],
                model=model.id,
                temperature=0.0
            )
            
            response = provider.generate(req)
            content = response.content.strip()
            # Basic parsing of JSON block if markdown is included
            if "{" in content and "}" in content:
                content = content[content.find("{"):content.rfind("}")+1]
                data = json.loads(content)
                return data.get("intent", "Unknown"), float(data.get("confidence", 0.5))
        except Exception as e:
            self.logger.error(f"LLM fallback failed: {e}")
            
        return "Unknown", 0.0

    def _ignore(self, reason: str) -> None:
        self.logger.info(f"IntentEngine: Ignored input ({reason})")
        self.event_bus.publish(
            Event(
                SystemEvents.INTENT_IGNORED,
                self.name,
                {"reason": reason},
            )
        )
