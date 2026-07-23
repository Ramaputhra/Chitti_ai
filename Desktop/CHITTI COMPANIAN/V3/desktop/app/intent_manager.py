from typing import Optional, Dict
from desktop.models.cognition import PendingIntent
import uuid
from datetime import datetime

class PendingIntentStore:
    """
    Manages incomplete planning decisions.
    Rule 194: Clarification Preserves Intent
    """
    def __init__(self):
        self._intents: Dict[str, PendingIntent] = {}
        
    def save(self, intent: PendingIntent):
        self._intents[intent.workflow_id] = intent
        
    def get(self, workflow_id: str) -> Optional[PendingIntent]:
        return self._intents.get(workflow_id)
        
    def remove(self, workflow_id: str):
        if workflow_id in self._intents:
            del self._intents[workflow_id]
            
    def get_by_correlation(self, correlation_id: str) -> Optional[PendingIntent]:
        for intent in self._intents.values():
            if intent.correlation_id == correlation_id:
                return intent
        return None
