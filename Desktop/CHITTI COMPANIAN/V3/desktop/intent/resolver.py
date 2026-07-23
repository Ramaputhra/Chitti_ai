import json
from pathlib import Path
from typing import Dict, Any

class EntityResolver:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.apps_dict = {}
        
    def load(self):
        apps_path = self.config_dir / "entities" / "applications.json"
        if apps_path.exists():
            with open(apps_path, 'r', encoding='utf-8') as f:
                self.apps_dict = json.load(f)
                
    def resolve(self, entities: Dict[str, str]) -> Dict[str, Any]:
        """
        Resolves abstract entities into concrete OS entities.
        Verifies existence where possible.
        """
        resolved = {}
        for key, value in entities.items():
            if key == "app_name":
                app_info = self.apps_dict.get(value)
                if app_info:
                    # Validate if it exists (mock logic)
                    concrete_exe = app_info["primary"]
                    if concrete_exe == "chrome.exe": # Mock: assume Chrome is installed
                        resolved[key] = concrete_exe
                    else:
                        resolved[key] = app_info.get("fallback") or "EntityNotFound"
                else:
                    resolved[key] = value
            else:
                resolved[key] = value
                
        return resolved
