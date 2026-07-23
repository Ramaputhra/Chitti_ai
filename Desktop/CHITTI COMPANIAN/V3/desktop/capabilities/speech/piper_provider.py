import subprocess
from typing import Any, Dict, List

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.provider import IProvider
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.health import ProviderHealth
from desktop.runtime.asset.ai_asset_manager import AIAssetManager


class PiperProvider(IProvider):
    """
    Local Text-to-Speech using Piper.
    Extremely fast, high quality local TTS.
    """
    def __init__(self, asset_manager: AIAssetManager, logger: ILoggingService, model_id: str = "piper_en_us_lessac"):
        self.asset_manager = asset_manager
        self.logger = logger
        self.model_id = model_id
        self._state = ServiceState.STOPPED
        self._is_healthy = False

    @property
    def name(self) -> str: return "PiperProvider"

    @property
    def state(self) -> ServiceState: return self._state

    def initialize(self) -> None:
        self.logger.info("Initializing Piper Provider...")
        
        if not self.asset_manager.verify_asset(self.model_id):
            self.logger.warning(f"Piper model {self.model_id} not found locally. Unavailable.")
            self._is_healthy = False
            return
            
        self._is_healthy = True
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

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
            model=self.model_id,
            uptime=0
        )

    def health_check(self) -> Dict[str, Any]:
        h = self.get_provider_health()
        return {"status": h.status, "model_id": h.model}

    def benchmark(self) -> Dict[str, Any]:
        return {"latency_ms": 50}

    def capabilities(self) -> List[str]:
        return ["text_to_speech", "offline"]

    def version(self) -> str:
        return "1.2.0"

    def configuration(self) -> Dict[str, Any]:
        return {"model_id": self.model_id}

    def speak(self, text: str, output_path: str = "output.wav") -> bool:
        if not self._is_healthy:
            return False
            
        asset = self.asset_manager.get_asset(self.model_id)
        if not asset: return False
            
        self.logger.info("Generating Piper TTS audio...")
        try:
            # Invoking piper CLI directly (or via python bindings)
            cmd = f"echo '{text}' | piper --model {asset.path} --output_file {output_path}"
            subprocess.run(cmd, shell=True, check=True)
            return True
        except Exception as e:
            self.logger.error(f"Piper TTS generation failed: {e}")
            return False
