import os
import json
import logging
from typing import Any, Dict, List
from desktop.platform.shared.interfaces.event_bus import IEventBus
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.provider import ProviderStatus
from desktop.platform.shared.interfaces.biometrics import ISpeakerVerifier
from desktop.platform.shared.models.biometrics import SpeakerState

logger = logging.getLogger(__name__)

class SherpaOnnxSpeakerVerifier(ISpeakerVerifier):
    def __init__(self, event_bus: IEventBus):
        self.event_bus = event_bus
        self._state = ServiceState.STOPPED
        self._is_loaded = False
        self.extractor = None
        self.reference_embeddings = []
        
        if hasattr(self.event_bus, "subscribe"):
            from desktop.platform.configuration.events import SystemEvents
            self.event_bus.subscribe(SystemEvents.VOICE_AUDIO_READY, self._on_audio_ready)

    @property
    def name(self) -> str:
        return "SherpaOnnxSpeakerVerifier"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self._load_voice_profiles()
        logger.info(f"{self.name} initialized")

    def _load_voice_profiles(self):
        try:
            profile_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'config', 'profiles')
            if os.path.exists(profile_dir):
                for f in os.listdir(profile_dir):
                    if f.endswith('_voice_profile.json'):
                        with open(os.path.join(profile_dir, f), 'r') as file:
                            data = json.load(file)
                            if 'embeddings' in data:
                                self.reference_embeddings.extend(data['embeddings'])
                logger.info(f"[SherpaOnnxSpeakerVerifier] Loaded {len(self.reference_embeddings)} reference embeddings.")
        except Exception as e:
            logger.error(f"Failed to load voice profiles: {e}")

    def _on_audio_ready(self, event):
        audio_data = event.payload.get("audio_buffer")
        if not audio_data:
            return
            
        state = self.verify(audio_data, self.reference_embeddings)
        
        if hasattr(self.event_bus, "publish"):
            from desktop.platform.configuration.events import SystemEvents
            self.event_bus.publish(Event(SystemEvents.VOICE_SPEAKER_VERIFIED, self.name, {
                "state": state.value,
                "confidence": 0.0 # Will add actual confidence soon if needed
            }))

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.unload_model()

    def health_check(self) -> Dict[str, Any]:
        return {"loaded": self._is_loaded}

    def benchmark(self) -> Dict[str, Any]:
        return {}

    def load_model(self, model_path: str) -> bool:
        logger.info(f"Loading Sherpa-ONNX speaker verification model from {model_path}...")
        try:
            import sherpa_onnx
            
            # Using standard initialization for sherpa-onnx speaker identification
            config = sherpa_onnx.SpeakerEmbeddingExtractorConfig(
                model=model_path,
                num_threads=1,
                debug=False,
            )
            self.extractor = sherpa_onnx.SpeakerEmbeddingExtractor(config)
            self._is_loaded = True
            return True
        except ImportError:
            logger.error("sherpa-onnx not installed. pip install sherpa-onnx")
            return False
        except Exception as e:
            logger.error(f"Failed to load Sherpa-ONNX model: {e}")
            return False

    def unload_model(self) -> None:
        self.extractor = None
        self._is_loaded = False

    def get_status(self) -> ProviderStatus:
        if not self._is_loaded:
            return ProviderStatus.DEGRADED
        return ProviderStatus.HEALTHY

    def extract_embedding(self, audio_data: bytes) -> List[float]:
        if not self._is_loaded or not self.extractor:
            logger.error("Sherpa-ONNX model not loaded.")
            return []
            
        import numpy as np
        # Convert raw bytes to normalized float32 array
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        try:
            import sherpa_onnx
            stream = self.extractor.create_stream()
            stream.accept_waveform(sample_rate=16000, waveform=audio_array)
            
            embedding = self.extractor.compute(stream)
            return np.array(embedding).tolist()
        except Exception as e:
            logger.error(f"Error extracting embedding: {e}")
            return []

    def verify(self, audio_data: bytes, reference_embeddings: List[List[float]], threshold: float = 0.6) -> SpeakerState:
        current_embedding = self.extract_embedding(audio_data)
        if not current_embedding or not reference_embeddings:
            return SpeakerState.UNKNOWN
            
        import numpy as np
        curr_arr = np.array(current_embedding)
        
        # Calculate cosine similarity against all known embeddings
        best_score = 0.0
        for ref in reference_embeddings:
            ref_arr = np.array(ref)
            score = np.dot(curr_arr, ref_arr) / (np.linalg.norm(curr_arr) * np.linalg.norm(ref_arr))
            if score > best_score:
                best_score = score
                
        logger.info(f"[Sherpa-ONNX] Speaker verification score: {best_score:.3f} (Threshold: {threshold})")
        
        if best_score >= threshold:
            return SpeakerState.VERIFIED
        else:
            return SpeakerState.REJECTED
