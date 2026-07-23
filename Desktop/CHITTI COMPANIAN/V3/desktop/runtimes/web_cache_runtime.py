import time
from typing import Optional, Dict, Any
from desktop.models.web_models import WebCollection

class WebCacheRuntime:
    """
    Caches fetched pages, search results, extracted markdown, and images metadata.
    Reduces bandwidth, avoids rate limits, and improves ACA performance.
    """
    
    def __init__(self, default_ttl_seconds: int = 3600):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl_seconds
        
    def _generate_key(self, resource_type: str, url: str) -> str:
        return f"{resource_type}:{url}"
        
    def get(self, resource_type: str, url: str) -> Optional[Any]:
        key = self._generate_key(resource_type, url)
        entry = self._cache.get(key)
        
        if not entry:
            return None
            
        if time.time() > entry["expires_at"]:
            del self._cache[key]
            return None
            
        return entry["data"]
        
    def set(self, resource_type: str, url: str, data: Any, ttl_seconds: Optional[int] = None):
        key = self._generate_key(resource_type, url)
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        
        self._cache[key] = {
            "data": data,
            "expires_at": time.time() + ttl
        }
        
    def invalidate(self, resource_type: str, url: str):
        key = self._generate_key(resource_type, url)
        if key in self._cache:
            del self._cache[key]
