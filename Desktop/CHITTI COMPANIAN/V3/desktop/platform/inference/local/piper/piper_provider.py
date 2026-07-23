import subprocess
from typing import Any, Dict, List, Generator

from desktop.platform.shared.interfaces.asset_manager import IAIAssetManager, AssetType
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.provider import IProvider, ProviderStatus
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.health import ProviderHealth
from desktop.runtime.asset.ai_asset_manager import AIAssetManager


from desktop.platform.shared.interfaces.speech import ISpeechSynthesizer

class PiperProvider(ISpeechSynthesizer):
    """
    Local Text-to-Speech using Piper.
    Extremely fast, high quality local TTS.
    """
    def __init__(self, asset_manager: IAIAssetManager, logger: ILoggingService):
        self.asset_manager = asset_manager
        self.logger = logger
        # Voice Registry (Language to Model ID mapping)
        self.voice_registry: Dict[str, str] = {
            "en": "piper_en_us_lessac",
            "te": "piper_te_in_anu"
        }
        self.default_model_id = self.voice_registry["en"]
        self._state = ServiceState.STOPPED
        self._is_healthy = False

    @property
    def name(self) -> str: return "PiperProvider"

    @property
    def state(self) -> ServiceState: return self._state

    def initialize(self) -> None:
        self.logger.info("Initializing Piper Provider...")
        
        if not self.asset_manager.verify_asset(self.default_model_id):
            self.logger.warning(f"Piper default model {self.default_model_id} not found locally. Unavailable.")
            self._is_healthy = False
            return
            
        self._is_healthy = True
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        
    def start(self) -> None:
        if self._state == ServiceState.STOPPED and self._is_healthy:
            self._state = ServiceState.RUNNING

    def pause(self) -> None:
        self._state = ServiceState.STOPPED

    def resume(self) -> None:
        if self._is_healthy:
            self._state = ServiceState.RUNNING

    def recover(self) -> None:
        self.shutdown()
        self.initialize()
        self.start()

    def get_provider_health(self) -> ProviderHealth:
        return ProviderHealth(
            status="Healthy" if self._is_healthy else "Unavailable",
            healthy=self._is_healthy,
            enabled=True,
            configured=True,
            authenticated=True,
            latency_ms=50,
            last_error=None,
            version="1.2.0",
            model=self.default_model_id,
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
        return {"latency_ms": 50}

    def capabilities(self) -> List[str]:
        return ["text_to_speech", "offline"]

    def version(self) -> str:
        return "1.2.0"

    def configuration(self) -> Dict[str, Any]:
        return {"default_model_id": self.default_model_id, "supported_languages": list(self.voice_registry.keys())}

    def _get_model_id_for_language(self, language: str) -> str:
        model_id = self.voice_registry.get(language, self.default_model_id)
        if not self.asset_manager.verify_asset(model_id):
            self.logger.warning(f"Voice model {model_id} for language '{language}' is missing. Falling back to default.")
            return self.default_model_id
        return model_id

    def synthesize(self, text: str, language: str = "en") -> bytes:
        if not self._is_healthy:
            return b""
            
        model_id = self._get_model_id_for_language(language)
        model_path = self.asset_manager.get_asset_path(AssetType.PIPER, model_id)
        
        self.logger.info(f"Synthesizing speech via Piper (lang: {language}, model: {model_id})...")
        try:
            cmd = ["piper", "--model", model_path, "--output_raw"]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout_data, stderr_data = process.communicate(input=text.encode('utf-8'))
            
            if process.returncode != 0:
                self.logger.error(f"Piper failed: {stderr_data.decode()}")
                return b""
                
            return stdout_data
        except Exception as e:
            self.logger.error(f"Failed to execute Piper: {e}")
            return b""

    def synthesize_stream(self, text: str, language: str = "en") -> Generator[bytes, None, None]:
        if not self._is_healthy:
            yield b""
            return
            
        model_id = self._get_model_id_for_language(language)
        model_path = self.asset_manager.get_asset_path(AssetType.PIPER, model_id)
        
        self.logger.info(f"Streaming speech via Piper (lang: {language}, model: {model_id})...")
        try:
            cmd = ["piper", "--model", model_path, "--output_raw"]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            process.stdin.write(text.encode('utf-8'))
            process.stdin.close()
            
            while True:
                chunk = process.stdout.read(4096)
                if not chunk:
                    break
                yield chunk
                
            process.wait()
            if process.returncode != 0:
                stderr = process.stderr.read().decode()
                self.logger.error(f"Piper streaming failed: {stderr}")
                
        except Exception as e:
            self.logger.error(f"Failed to stream Piper: {e}")
            yield b""
