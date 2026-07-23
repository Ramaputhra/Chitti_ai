import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AssetRegistry:
    """S36D-1: UI Asset Registry (Icons, Vectors, Themes)."""
    def __init__(self):
        self._registry: Dict[str, str] = {}

    def register(self, asset_id: str, path: str):
        self._registry[asset_id] = path

    def get(self, asset_id: str) -> str:
        return self._registry.get(asset_id, "")
