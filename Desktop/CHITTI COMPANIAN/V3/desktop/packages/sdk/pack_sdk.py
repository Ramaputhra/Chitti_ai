import json
from typing import Dict, List, Any
from abc import ABC, abstractmethod

class PackManifest:
    """Declarative pack configuration loaded from manifest.json."""
    def __init__(self, manifest_path: str):
        with open(manifest_path, 'r') as f:
            data = json.load(f)
        self.id = data.get("id", "")
        self.name = data.get("name", "")
        self.version = data.get("version", "")
        self.description = data.get("description", "")
        
        # Declarative registries
        self.capabilities = data.get("capabilities", [])
        self.skills = data.get("skills", [])
        self.recipes = data.get("recipes", [])
        self.experiences = data.get("experiences", [])
        self.knowledge = data.get("knowledge", [])
        self.widgets = data.get("widgets", [])
        self.events = data.get("events", [])
        self.automation_workflows = data.get("automation_workflows", [])

class Pack(ABC):
    """
    Generic Pack SDK.
    All packs inherit this to participate in the standardized CHITTI lifecycle.
    """
    def __init__(self, manifest_path: str):
        self.manifest = PackManifest(manifest_path)
        
    def initialize(self):
        """Called upon load to setup internal state."""
        pass
        
    def install(self):
        """Called upon first installation."""
        pass
        
    def enable(self):
        """Called when the user turns the pack on."""
        pass
        
    def disable(self):
        """Called when the user turns the pack off."""
        pass
        
    def upgrade(self, previous_version: str):
        """Called when upgrading from an older version."""
        pass
        
    def uninstall(self):
        """Called upon permanent removal."""
        pass
        
    def shutdown(self):
        """Called upon graceful platform shutdown."""
        pass
