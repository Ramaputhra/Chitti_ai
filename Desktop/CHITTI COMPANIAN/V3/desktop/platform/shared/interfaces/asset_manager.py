from enum import Enum
from typing import Dict, List, Optional

from desktop.platform.shared.interfaces.service import IService


class AssetType(Enum):
    WHISPER = "WHISPER"
    PIPER = "PIPER"
    LLM = "LLM"
    EMBEDDING = "EMBEDDING"
    VISION = "VISION"


class IAIAssetManager(IService):
    """
    Centralizes the management of all physical model weights on disk.
    """
    def get_asset_path(self, asset_type: AssetType, model_name: str) -> Optional[str]:
        ...

    def register_asset(self, asset_type: AssetType, model_name: str, path: str) -> None:
        ...

    def list_assets(self, asset_type: AssetType = None) -> Dict[str, List[str]]:
        ...

    def list_manifests(self) -> List[Dict[str, Any]]:
        ...

    def verify_asset(self, relative_path: str) -> bool:
        ...
