from dataclasses import dataclass
from typing import List, Dict, Any

# Read-only configuration schemas. 
# In a real implementation, we'd use pydantic for robust type checking.
# For now, we use standard dataclasses with a manual validate staticmethod.

@dataclass(frozen=True)
class NormalizationSchema:
    mappings: Dict[str, List[str]]
    
    @staticmethod
    def validate(data: Dict[str, Any]):
        if "mappings" not in data or not isinstance(data["mappings"], dict):
            raise ValueError("Invalid NormalizationSchema: missing mappings dict")

@dataclass(frozen=True)
class IntentSchema:
    intent_id: str
    aliases: List[str]
    priority: int
    requires_authentication: bool
    version: int
    
    @staticmethod
    def validate(data: Dict[str, Any]):
        required = ["intent_id", "aliases", "priority", "requires_authentication", "version"]
        for req in required:
            if req not in data:
                raise ValueError(f"Invalid IntentSchema: missing {req}")

@dataclass(frozen=True)
class WorkflowSchema:
    workflow_id: str
    version: int
    steps: List[str]
    
    @staticmethod
    def validate(data: Dict[str, Any]):
        required = ["workflow_id", "version", "steps"]
        for req in required:
            if req not in data:
                raise ValueError(f"Invalid WorkflowSchema: missing {req}")
