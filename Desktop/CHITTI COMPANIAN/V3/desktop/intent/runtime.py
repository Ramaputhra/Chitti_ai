import asyncio
import json
import time
import hashlib
from pathlib import Path
from typing import Callable
from desktop.core.runtime import (
    IRuntime, RuntimeMetadata, RuntimePriority, RuntimeTraits,
    HealthPolicy, RestartPolicy, RuntimeState, HealthPayload
)
from desktop.models.events import SystemEvent
from desktop.speech.models import SpeechTranscribed
from desktop.intent.models import IntentRecognized, IntentClarificationRequired, IntentUnknown, IntentMetadata, IntentTrace
from desktop.intent.normalizer import TextNormalizer
from desktop.intent.registry import LocalIntentRegistry
from desktop.intent.matcher import IntentMatcher
from desktop.intent.extractor import EntityExtractor
from desktop.intent.resolver import EntityResolver
from desktop.intent.validator import IntentValidator
from datetime import datetime, timezone

class IntentRuntime(IRuntime):
    def __init__(self, publish_event: Callable[[SystemEvent], None], config_dir: Path):
        self._publish = publish_event
        self.config_dir = config_dir
        self._state = RuntimeState.CREATED
        self._health = HealthPayload(True, self._state, datetime.now(timezone.utc), 0.0)
        
        self._metadata = RuntimeMetadata(
            runtime_id="IntentRuntime",
            api_version="1.0",
            priority=RuntimePriority.HIGH, 
            dependencies=["SpeechRuntime"],
            traits=RuntimeTraits(background=True),
            health_policy=HealthPolicy(interval_seconds=2.0),
            restart_policy=RestartPolicy.ALWAYS
        )
        
        self._normalizer = TextNormalizer(config_dir)
        self._registry = LocalIntentRegistry(config_dir)
        self._matcher = IntentMatcher(self._registry)
        self._extractor = EntityExtractor()
        self._resolver = EntityResolver(config_dir)
        self._validator = IntentValidator()
        self._clarifications = {}
        
    def get_metadata(self) -> RuntimeMetadata:
        return self._metadata
        
    def get_state(self) -> RuntimeState:
        return self._state
        
    async def initialize(self) -> None:
        self._state = RuntimeState.INITIALIZING
        self._reload_configurations()
        self._state = RuntimeState.READY
        
    def _reload_configurations(self):
        self._normalizer.load()
        self._registry.load()
        self._resolver.load()
        
        clarif_path = self.config_dir / "clarifications.json"
        if clarif_path.exists():
            with open(clarif_path, 'r', encoding='utf-8') as f:
                self._clarifications = json.load(f)
        
    async def start(self) -> None:
        self._state = RuntimeState.RUNNING
        
    async def stop(self) -> None:
        self._state = RuntimeState.STOPPED
        
    async def health_check(self) -> HealthPayload:
        self._health.state = self._state
        self._health.last_heartbeat = datetime.now(timezone.utc)
        return self._health

    def _generate_hash(self, text: str, timestamp: float) -> str:
        data = f"{text}_{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

    async def handle_speech_transcribed(self, event: SpeechTranscribed) -> None:
        if self._state != RuntimeState.RUNNING:
            return
            
        start_time = time.time()
        text = event.text
        
        canonical_text = self._normalizer.normalize(text)
        intent_id, confidence = self._matcher.match(canonical_text)
        
        if not intent_id:
            self._publish(IntentUnknown(text=text))
            return
            
        if confidence < 0.75:
            self._publish(IntentUnknown(text=text))
            return
            
        if 0.75 <= confidence < 0.95:
            prompt = self._clarifications.get(intent_id, ["Could you please clarify?"])[0]
            self._publish(IntentClarificationRequired(intent_id=intent_id, prompt=prompt))
            return
            
        raw_entities = self._extractor.extract(intent_id, canonical_text)
        concrete_entities = self._resolver.resolve(raw_entities)
        
        definition = self._registry.get_definition(intent_id)
        if not self._validator.validate(intent_id, definition.metadata, concrete_entities):
            self._publish(IntentUnknown(text=text))
            return
            
        duration_ms = (time.time() - start_time) * 1000.0
        intent_hash = self._generate_hash(text, start_time)
        
        trace = IntentTrace(
            original_text=text,
            normalized_text=canonical_text,
            matched_intent=intent_id,
            confidence=confidence,
            resolved_entities=concrete_entities,
            registry_source="core"
        )
        
        self._publish(IntentRecognized(
            intent_id=intent_id,
            intent_hash=intent_hash,
            category=definition.category,
            metadata=definition.metadata,
            entities=concrete_entities,
            confidence=confidence,
            source="core",
            language=event.language,
            duration_ms=duration_ms,
            trace=trace
        ))
