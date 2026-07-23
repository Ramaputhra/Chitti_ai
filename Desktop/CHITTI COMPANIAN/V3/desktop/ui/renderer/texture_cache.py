import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class TextureCache:
    """
    S36D-1: GPU Texture Cache preventing repeated image decoding.
    """
    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)

    def put(self, key: str, texture: Any):
        self._cache[key] = texture
        logger.info(f"[TextureCache] Cached texture '{key}'")

    def clear(self):
        self._cache.clear()
