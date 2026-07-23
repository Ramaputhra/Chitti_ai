from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from desktop.platform.shared.interfaces.asset_manager import IAIAssetManager
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import IService, ServiceState

@dataclass
class ModelManifest:
    id: str
    type: str  # llm, speech, vision, ocr, embedding, reranker
    runtime: str # ollama, llama_cpp, faster_whisper, piper
    family: str
    parameters: str
    context_window: int
    memory_gb: float
    languages: List[str]
    vision: bool
    tool_use: bool
    streaming: bool
    license: str
    recommended_tasks: List[str]
    version: str
    size_gb: float
    capabilities: List[str]
    relative_path: Optional[str] = None

class ModelRegistry(IService):
    """
    Discovers, validates, and serves metadata for all available AI models 
    based on manifests. Keeps Provider selection logic cleanly separated.
    """
    def __init__(self, asset_manager: IAIAssetManager, logger: ILoggingService) -> None:
        self.asset_manager = asset_manager
        self.logger = logger
        self._state = ServiceState.STOPPED
        self._models: Dict[str, ModelManifest] = {}

    @property
    def name(self) -> str: return "ModelRegistry"

    @property
    def state(self) -> ServiceState: return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self._discover_models()

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> Dict[str, Any]:
        return {"status": "Healthy", "models_registered": len(self._models)}

    def _discover_models(self) -> None:
        manifest_data = self.asset_manager.list_manifests()
        for data in manifest_data:
            try:
                manifest = ModelManifest(
                    id=data["id"],
                    type=data["type"],
                    runtime=data["runtime"],
                    family=data.get("family", "unknown"),
                    parameters=data.get("parameters", "0B"),
                    context_window=data.get("context_window", 4096),
                    memory_gb=data.get("memory_gb", 0.0),
                    languages=data.get("languages", ["en"]),
                    vision=data.get("vision", False),
                    tool_use=data.get("tool_use", False),
                    streaming=data.get("streaming", False),
                    license=data.get("license", "unknown"),
                    recommended_tasks=data.get("recommended_tasks", []),
                    version=data.get("version", "1.0"),
                    size_gb=data.get("size_gb", 0.0),
                    capabilities=data.get("capabilities", []),
                    relative_path=data.get("relative_path")
                )
                self.register_model(manifest)
            except Exception as e:
                self.logger.warning(f"Invalid manifest data {data}: {e}")

    def register_model(self, manifest: ModelManifest) -> None:
        # If it's a file-based model (e.g. llama_cpp), verify it exists
        if manifest.relative_path:
            if not self.asset_manager.verify_asset(manifest.relative_path):
                self.logger.warning(f"Model {manifest.id} listed in manifest but file not found at {manifest.relative_path}")
                return
        
        self._models[manifest.id] = manifest
        self.logger.info(f"Registered Model: {manifest.id} ({manifest.type}) via {manifest.runtime}")

    def get_model(self, model_id: str) -> Optional[ModelManifest]:
        return self._models.get(model_id)

    def find_models_by_capability(self, capability: str) -> List[ModelManifest]:
        return [m for m in self._models.values() if capability in m.capabilities]
