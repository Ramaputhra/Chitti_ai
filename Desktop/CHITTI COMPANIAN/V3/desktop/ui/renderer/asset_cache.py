import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AssetCache:
    """
    S36D-1: SVG & Asset Cache supporting Lazy Loading & Asset Hot Reload.
    """
    def __init__(self):
        self._assets: Dict[str, Any] = {}

    def get_asset(self, path: str) -> Optional[Any]:
        return self._assets.get(path)

    def cache_asset(self, path: str, content: Any):
        self._assets[path] = content

    def reload(self):
        self._assets.clear()
        logger.info("[AssetCache] Asset Cache hot-reloaded cleanly.")
