from typing import Dict, Any

class EntityExtractor:
    def extract(self, intent_id: str, canonical_text: str) -> Dict[str, str]:
        """
        Extracts raw entities from the text based on the intent.
        For example, pulling 'browser' out of 'browser open'.
        """
        entities = {}
        if intent_id == "OPEN_APPLICATION" and "browser" in canonical_text:
            entities["app_name"] = "browser"
        elif intent_id == "OPEN_APPLICATION" and "notepad" in canonical_text:
            entities["app_name"] = "notepad"
            
        return entities
