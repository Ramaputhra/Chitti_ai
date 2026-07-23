import asyncio
from typing import Dict, List, Callable
from desktop.core.runtime import (
    IRuntime, RuntimeMetadata, RuntimePriority, RuntimeTraits,
    HealthPolicy, RestartPolicy, RuntimeState, HealthPayload
)
from desktop.models.events import SystemEvent
from desktop.speech.models import SpeechTranscribed, SpeakerVerified
from desktop.speech.auth import ISpeakerVerifier, ECAPATDNNVerifier
from desktop.speech.vad import SileroVAD
from desktop.speech.detector import LanguageDetector
from desktop.speech.providers.base import ISTTProvider
from desktop.speech.providers.english_stt import EnglishSTTProvider
from desktop.speech.providers.indic_conformer import IndicConformerProvider
from datetime import datetime, timezone

class SpeechRuntime(IRuntime):
    def __init__(self, publish_event: Callable[[SystemEvent], None]):
        self._publish = publish_event
        self._state = RuntimeState.CREATED
        self._health = HealthPayload(True, self._state, datetime.now(timezone.utc), 0.0)
        
        self._metadata = RuntimeMetadata(
            runtime_id="SpeechRuntime",
            api_version="1.0",
            priority=RuntimePriority.HIGH, # Input runtimes boot early
            dependencies=[],
            traits=RuntimeTraits(background=True),
            health_policy=HealthPolicy(interval_seconds=2.0),
            restart_policy=RestartPolicy.ALWAYS
        )
        
        # Internal Pipeline Components
        self._vad = SileroVAD()
        self._detector = LanguageDetector()
        self._auth = ECAPATDNNVerifier()
        self._providers: Dict[str, ISTTProvider] = {}
        self._is_listening = False
        self._listen_task = None
        
    def get_metadata(self) -> RuntimeMetadata:
        return self._metadata
        
    def get_state(self) -> RuntimeState:
        return self._state
        
    async def initialize(self) -> None:
        self._state = RuntimeState.INITIALIZING
        
        # Load Providers
        en_provider = EnglishSTTProvider()
        en_provider.load()
        for lang in en_provider.get_supported_languages():
            self._providers[lang] = en_provider
            
        te_provider = IndicConformerProvider()
        te_provider.load()
        for lang in te_provider.get_supported_languages():
            self._providers[lang] = te_provider
            
        self._state = RuntimeState.READY
        
    async def start(self) -> None:
        self._state = RuntimeState.RUNNING
        self._is_listening = True
        self._listen_task = asyncio.create_task(self._microphone_loop())
        
    async def stop(self) -> None:
        self._state = RuntimeState.STOPPING
        self._is_listening = False
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        self._state = RuntimeState.STOPPED
        
    async def health_check(self) -> HealthPayload:
        self._health.state = self._state
        self._health.last_heartbeat = datetime.now(timezone.utc)
        return self._health
        
    async def _microphone_loop(self):
        # Mocking a continuous audio stream
        while self._is_listening:
            try:
                await asyncio.sleep(1.0)
                mock_audio = b"dummy_pcm_data"
                
                # Pipeline Step 1: Voice Authentication
                auth_result = await self._auth.verify(mock_audio)
                self._publish(auth_result)
                
                # Pipeline Step 2: VAD
                if not self._vad.is_speech(mock_audio):
                    continue
                    
                # Pipeline Step 3: Language Detection
                lang = self._detector.detect_language(mock_audio)
                
                # Pipeline Step 4: Provider Routing & Transcription
                provider = self._providers.get(lang)
                if provider:
                    result = await provider.transcribe_stream(mock_audio)
                    if result:
                        self._publish(result)
                else:
                    print(f"[SpeechRuntime] No provider found for detected language: {lang}")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[SpeechRuntime] Error in microphone loop: {e}")
