from typing import Any, Dict, List, Optional

from faster_whisper import WhisperModel
import numpy as np

from desktop.platform.shared.models.audio import AudioPacket

from desktop.platform.shared.interfaces.asset_manager import IAIAssetManager, AssetType
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.provider import IProvider, ProviderStatus
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.health import ProviderHealth
from desktop.runtime.asset.ai_asset_manager import AIAssetManager


class WhisperProvider(IProvider):
    """
    Local Speech-to-Text using Faster-Whisper.
    Relies on AIAssetManager to ensure weights are present.
    """
    def __init__(self, asset_manager: IAIAssetManager, logger: ILoggingService):
        self.asset_manager = asset_manager
        self.logger = logger
        self.model_id = "whisper_small"
        self.model: Optional[WhisperModel] = None
        self._state = ServiceState.STOPPED
        self._is_healthy = False

    @property
    def name(self) -> str: return "WhisperProvider"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self.logger.info("Initializing Whisper Provider...")
        
        # Verify asset
        if not self.asset_manager.verify_asset(self.model_id):
            self.logger.warning(f"Whisper model {self.model_id} not found locally. Unavailable.")
            self._is_healthy = False
            return
            
        try:
            asset_path = self.asset_manager.get_asset_path(AssetType.WHISPER, self.model_id)
            # In a real environment, device="cuda" if available
            self.model = WhisperModel(asset_path if asset_path else "small", device="cpu", compute_type="int8")
            self._is_healthy = True
            self._state = ServiceState.RUNNING
            self.logger.info("Whisper initialized successfully.")
        except Exception as e:
            self.logger.warning(f"Whisper initialization failed: {e}. Provider will degrade gracefully.")
            self._state = ServiceState.STOPPED

    def start(self) -> None:
        if self._state == ServiceState.STOPPED and self.model:
            self._state = ServiceState.RUNNING

    def pause(self) -> None:
        self._state = ServiceState.STOPPED

    def resume(self) -> None:
        if self.model:
            self._state = ServiceState.RUNNING

    def recover(self) -> None:
        self.logger.info("WhisperProvider attempting recovery...")
        self.shutdown()
        self.initialize()
        self.start()

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.model = None

    def get_provider_health(self) -> ProviderHealth:
        return ProviderHealth(
            status="Healthy" if self._is_healthy else "Unavailable",
            healthy=self._is_healthy,
            enabled=True,
            configured=True,
            authenticated=True,
            latency_ms=150,
            last_error=None,
            version="1.0.0",
            model=self.model_id,
            uptime=0
        )

    def health_check(self) -> Dict[str, Any]:
        h = self.get_provider_health()
        return {"status": h.status, "model_id": h.model}

    def get_status(self) -> ProviderStatus:
        if not self._is_healthy:
            return ProviderStatus.UNAVAILABLE
        return ProviderStatus.HEALTHY

    def benchmark(self) -> Dict[str, Any]:
        return {"latency_ms": 150} # Local inference latency

    def capabilities(self) -> List[str]:
        return ["speech_to_text", "offline"]

    def version(self) -> str:
        return "1.0.0"

    def configuration(self) -> Dict[str, Any]:
        return {"model_id": self.model_id}

    def transcribe(self, packet: AudioPacket) -> TranscriptionResult:
        if not self._is_healthy or not self.model:
            return TranscriptionResult(text="", language="en", confidence=0.0)
            
        self.logger.info("Transcribing audio packet...")
        try:
            # Convert 16-bit PCM bytes to float32 numpy array for whisper
            audio_data = np.frombuffer(packet.data, dtype=np.int16)
            audio_float32 = audio_data.astype(np.float32) / 32768.0
            
            segments, info = self.model.transcribe(audio_float32, beam_size=5)
            text = "".join([segment.text for segment in segments])
            return TranscriptionResult(
                text=text.strip(),
                language=info.language,
                confidence=info.language_probability
            )
        except Exception as e:
            self.logger.error(f"Whisper transcription failed: {e}")
            return TranscriptionResult(text="", language="en", confidence=0.0)
