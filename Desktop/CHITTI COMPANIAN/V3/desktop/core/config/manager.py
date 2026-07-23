import json
from pathlib import Path
from typing import Dict, Any, Type, TypeVar
from desktop.core.config.schema import IntentSchema, WorkflowSchema, NormalizationSchema

T = TypeVar('T')

class ConfigManager:
    """
    Centralized Configuration Manager enforcing Rule 245.
    Loads JSON, validates schemas, and returns read-only objects.
    """
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self._cache = {}
        
    def load_and_validate(self, filename: str, schema_class: Type[T]) -> T:
        if filename in self._cache:
            return self._cache[filename]
            
        filepath = self.config_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file {filepath} not found.")
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Basic schema validation (mocking pydantic/marshmallow for zero-dependency Phase 4)
        if hasattr(schema_class, 'validate'):
            schema_class.validate(data)
            
        # Freeze data into schema object
        obj = schema_class(**data)
        self._cache[filename] = obj
        return obj

    def clear_cache(self):
        self._cache.clear()
