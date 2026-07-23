from typing import Optional, Dict
from desktop.models.reasoning import ReasoningPlan
import time
import hashlib

class ReasoningCache:
    """
    Caches deterministic Intent -> ReasoningPlan to avoid re-evaluating rules on repeat commands.
    """
    def __init__(self, ttl_seconds: int = 600):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, dict] = {}

    def _hash_intent(self, intent: str, context_hash: str = "") -> str:
        key = f"{intent}_{context_hash}"
        return hashlib.md5(key.encode()).hexdigest()

    def get(self, intent: str, context_hash: str = "") -> Optional[ReasoningPlan]:
        key = self._hash_intent(intent, context_hash)
        entry = self._cache.get(key)
        
        if entry:
            if time.time() - entry["timestamp"] < self.ttl_seconds:
                return entry["plan"]
            else:
                del self._cache[key]
                
        return None

    def set(self, intent: str, plan: ReasoningPlan, context_hash: str = ""):
        key = self._hash_intent(intent, context_hash)
        self._cache[key] = {
            "timestamp": time.time(),
            "plan": plan
        }
