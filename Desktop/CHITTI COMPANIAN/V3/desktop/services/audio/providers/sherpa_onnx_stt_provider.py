import os
import json
import logging
from typing import Any, Dict
from desktop.platform.shared.interfaces.event_bus import IEventBus, Event
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.provider import ProviderStatus
from desktop.platform.shared.interfaces.speech import ISpeechProvider
from desktop.platform.shared.models.audio import AudioPacket, TranscriptionResult
from desktop.platform.configuration.events import SystemEvents

logger = logging.getLogger(__name__)

class SherpaOnnxSTTProvider(ISpeechProvider):
    def __init__(self, event_bus: IEventBus):
        self.event_bus = event_bus
        self._state = ServiceState.STOPPED
        self._is_loaded = False
        self.recognizer = None
        
        if hasattr(self.event_bus, "subscribe"):
            # We don't subscribe to VOICE_AUDIO_READY directly here anymore, 
            # SpeechRouter/LanguageDetector should handle routing.
            pass

    @property
    def name(self) -> str:
        return "SherpaOnnxSTTProvider"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.unload_model()

    def health_check(self) -> Dict[str, Any]:
        return {"loaded": self._is_loaded}

    def benchmark(self) -> Dict[str, Any]:
        return {}

    def load_model(self, model_path: str) -> bool:
        logger.info(f"Loading Sherpa-ONNX STT model from {model_path}...")
        try:
            import sherpa_onnx
            
            # Simplified initialization for offline recognizer
            # Expects a path to a directory containing the model files or a specific config
            recognizer_config = sherpa_onnx.OfflineRecognizerConfig(
                feat_config=sherpa_onnx.FeatureConfig(sample_rate=16000, feature_dim=80),
                model_config=sherpa_onnx.OfflineModelConfig(
                    transducer=sherpa_onnx.OfflineTransducerModelConfig(
                        encoder=f"{model_path}/encoder.onnx",
                        decoder=f"{model_path}/decoder.onnx",
                        joiner=f"{model_path}/joiner.onnx",
                    ),
                    tokens=f"{model_path}/tokens.txt",
                    num_threads=1,
                    debug=False,
                )
            )
            
            self.recognizer = sherpa_onnx.OfflineRecognizer(recognizer_config)
            self._is_loaded = True
            logger.info("Sherpa-ONNX STT model loaded successfully.")
            return True
        except ImportError:
            logger.error("sherpa-onnx not installed. Run: pip install sherpa-onnx")
            return False
        except Exception as e:
            logger.error(f"Failed to load Sherpa-ONNX STT model: {e}")
            return False

    def unload_model(self) -> None:
        self.recognizer = None
        self._is_loaded = False

    def get_status(self) -> ProviderStatus:
        if not self._is_loaded:
            return ProviderStatus.DEGRADED
        return ProviderStatus.HEALTHY

    def transcribe(self, packet: AudioPacket) -> TranscriptionResult:
        if not self._is_loaded or not self.recognizer:
            logger.error("Sherpa-ONNX STT model not loaded.")
            return TranscriptionResult(text="", confidence=0.0, language="unknown")
            
        import numpy as np
        # Convert raw bytes to normalized float32 array for 16kHz
        audio_array = np.frombuffer(packet.data, dtype=np.int16).astype(np.float32) / 32768.0
        
        try:
            import sherpa_onnx
            stream = self.recognizer.create_stream()
            stream.accept_waveform(sample_rate=16000, waveform=audio_array)
            
            self.recognizer.decode_stream(stream)
            result = stream.result.text
            
            # Note: Sherpa-ONNX does not typically return a standard confidence float natively in the text result without extra config, 
            # we will set a default or dummy confidence for now.
            confidence = 0.90 if result else 0.0
            language = packet.metadata.get("language", "hi") # Defaulting to Indic/Hindi assumption for this provider
            
            if result and hasattr(self.event_bus, "publish"):
                self.event_bus.publish(Event(SystemEvents.LANGUAGE_TEXT_RECOGNIZED, self.name, {"text": result, "language": language}))
                
            return TranscriptionResult(text=result, confidence=confidence, language=language)
        except Exception as e:
            logger.error(f"Error during Sherpa-ONNX transcription: {e}")
            return TranscriptionResult(text="", confidence=0.0, language="unknown")
