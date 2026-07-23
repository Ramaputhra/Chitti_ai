from typing import Dict, Any
from desktop.intent.models import IntentMetadata

class IntentValidator:
    def validate(self, intent_id: str, metadata: IntentMetadata, entities: Dict[str, Any]) -> bool:
        """
        Validates the intent before it is published.
        Returns True if valid and complete.
        """
        # Ensure required entities are found and not 'EntityNotFound'
        for k, v in entities.items():
            if v == "EntityNotFound":
                return False
                
        # More complex validation could go here, e.g., missing mandatory parameters
        if intent_id == "OPEN_APPLICATION" and not entities.get("app_name"):
            return False
            
        return True
