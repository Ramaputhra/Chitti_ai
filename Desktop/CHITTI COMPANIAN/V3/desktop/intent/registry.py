import json
from pathlib import Path
from typing import Dict, List
from desktop.intent.models import IntentDefinition, IntentMetadata

class LocalIntentRegistry:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.intent_defs: Dict[str, IntentDefinition] = {}
        
    def load(self):
        self.intent_defs.clear()
        
        core_path = self.config_dir / "intents" / "core_intents.json"
        if core_path.exists():
            with open(core_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for intent_id, properties in data.items():
                    self.intent_defs[intent_id] = IntentDefinition(
                        intent_id=intent_id,
                        category="System", # Mock category mapping for now
                        version=properties.get("version", 1),
                        priority=properties.get("priority", 0),
                        metadata=IntentMetadata(requires_authentication=True), # Mock meta
                        aliases=properties.get("aliases", [])
                    )
            
    def get_aliases(self, intent_id: str) -> List[str]:
        if intent_id in self.intent_defs:
            return self.intent_defs[intent_id].aliases
        return []
        
    def get_definition(self, intent_id: str) -> IntentDefinition:
        return self.intent_defs.get(intent_id)
