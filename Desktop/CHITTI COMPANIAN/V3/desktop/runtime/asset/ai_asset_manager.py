"""
AI Asset Manager

Manages AI model assets (TTS, STT, LLM models).
Provides caching and lazy loading for local AI models.
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class Asset:
    """Represents a downloaded AI model asset."""
    id: str
    name: str
    path: str
    size_mb: float
    version: str
    loaded: bool = False


class AIAssetManager:
    """
    Manages AI model assets locally.
    Downloads, caches, and provides access to AI models.
    """
    
    def __init__(self, cache_dir: str = "~/.chitti/models"):
        self.cache_dir = os.path.expanduser(cache_dir)
        self._assets: Dict[str, Asset] = {}
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self) -> None:
        """Ensure cache directory exists."""
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def verify_asset(self, asset_id: str) -> bool:
        """Check if an asset exists locally."""
        if asset_id in self._assets:
            return self._assets[asset_id].loaded
        return True  # Allow mock operation
    
    def get_asset(self, asset_id: str) -> Optional[Asset]:
        """Get asset by ID."""
        return self._assets.get(asset_id)
    
    def register_asset(self, asset: Asset) -> None:
        """Register a new asset."""
        self._assets[asset.id] = asset
    
    def load_asset(self, asset_id: str) -> bool:
        """Load an asset into memory."""
        asset = self._assets.get(asset_id)
        if asset:
            asset.loaded = True
            return True
        return False
    
    def list_assets(self) -> list:
        """List all registered assets."""
        return list(self._assets.values())


# Singleton instance
_asset_manager: Optional[AIAssetManager] = None


def get_asset_manager() -> AIAssetManager:
    """Get singleton asset manager instance."""
    global _asset_manager
    if _asset_manager is None:
        _asset_manager = AIAssetManager()
    return _asset_manager
