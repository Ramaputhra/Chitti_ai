from typing import Any, Dict, Generator

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.provider import ProviderStatus
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.speech import ISpeechProvider
from desktop.platform.integrations.core.provider_registry import SpeechProviderRegistry


class SpeechRouter(ISpeechProvider):
    def __init__(self, registry: SpeechProviderRegistry, logger: ILoggingService) -> None:
        self.registry = registry
        self.logger = logger
        self._state = ServiceState.STOPPED
        
        from desktop.services.audio.language_detector import LanguageDetector
        self.language_detector = LanguageDetector()

    @property
    def name(self) -> str:
        return "SpeechRouter"

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
        return {"registry_status": self.registry.health_check()}

    def benchmark(self) -> Dict[str, Any]:
        return {}

    def load_model(self, model_path: str) -> bool:
        return True

    def unload_model(self) -> None:
        pass

    def supports_streaming(self) -> bool:
        return True

    def supports_gpu(self) -> bool:
        return False

    def get_status(self) -> ProviderStatus:
        active = self.registry.get_active_providers()
        if not active:
            return ProviderStatus.UNAVAILABLE
        return ProviderStatus.HEALTHY

    def _get_best_provider(self, audio_data: bytes = None) -> ISpeechProvider:
        active = self.registry.get_active_providers()
        if not active:
            raise RuntimeError("No healthy ISpeechProvider available in registry.")
            
        # If we have audio data, detect language
        if audio_data and hasattr(self, 'language_detector'):
            lang = self.language_detector.detect(audio_data)
            self.logger.info(f"[SpeechRouter] Detected language: {lang}")
            
            # Simple routing logic
            if lang != "en":
                # Find sherpa for Indic languages
                for p in active:
                    if "Sherpa" in p.name:
                        return p
            else:
                # Find whisper for English
                for p in active:
                    if "Whisper" in p.name:
                        return p
                        
        # Default fallback
        return active[0]

    def process_audio(self, audio_data: bytes) -> str:
        provider = self._get_best_provider(audio_data)
        self.logger.info(f"SpeechRouter routing process_audio to {provider.name}")
        return provider.process_audio(audio_data)

    def process_audio_stream(
        self, audio_stream: Generator[bytes, None, None]
    ) -> Generator[str, None, None]:
        provider = self._get_best_provider()
        if not provider.supports_streaming():
            self.logger.warning(f"Provider {provider.name} does not support streaming. Falling back to block processing.")
            # Simplistic block fallback
            data = b"".join(list(audio_stream))
            yield provider.process_audio(data)
            return

        self.logger.info(f"SpeechRouter routing process_audio_stream to {provider.name}")
        yield from provider.process_audio_stream(audio_stream)
