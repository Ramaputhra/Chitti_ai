from typing import Optional, Dict
from desktop.models.retrieval import RetrievalQuery, ContextPackage
import hashlib
import time

class RetrievalCache:
    """
    Caches ContextPackages to prevent redundant queries (e.g. "Summarize today's productivity").
    """
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, dict] = {}

    def _hash_query(self, query: RetrievalQuery) -> str:
        # Create a deterministic hash of the query parameters
        key = f"{query.text}_{query.intent}_{query.workspace}_{query.strategy.value}"
        return hashlib.md5(key.encode()).hexdigest()

    def get(self, query: RetrievalQuery) -> Optional[ContextPackage]:
        key = self._hash_query(query)
        entry = self._cache.get(key)
        
        if entry:
            if time.time() - entry["timestamp"] < self.ttl_seconds:
                return entry["package"]
            else:
                del self._cache[key]
                
        return None

    def set(self, query: RetrievalQuery, package: ContextPackage):
        key = self._hash_query(query)
        self._cache[key] = {
            "timestamp": time.time(),
            "package": package
        }
