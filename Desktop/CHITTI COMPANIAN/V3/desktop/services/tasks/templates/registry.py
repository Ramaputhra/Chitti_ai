import os
import yaml
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

from desktop.platform.shared.models.template import (
    TaskTemplateDescriptor, 
    TemplateNode, 
    CompiledTemplate, 
    TemplateContext
)
from desktop.platform.shared.interfaces.logging import ILoggingService

class ITemplateProvider(ABC):
    @abstractmethod
    def load_templates(self) -> List[Dict[str, Any]]:
        pass

class LocalTemplateProvider(ITemplateProvider):
    def __init__(self, templates_dir: str):
        self.templates_dir = templates_dir

    def load_templates(self) -> List[Dict[str, Any]]:
        templates = []
        if not os.path.exists(self.templates_dir):
            return templates
            
        for root, _, files in os.walk(self.templates_dir):
            for file in files:
                if file.endswith(".yaml") or file.endswith(".yml"):
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8') as f:
                        try:
                            data = yaml.safe_load(f)
                            if data:
                                templates.append(data)
                        except Exception as e:
                            print(f"Error loading template {path}: {e}")
        return templates

class TemplateRegistry:
    def __init__(self, logger: ILoggingService):
        self._logger = logger
        self._providers: List[ITemplateProvider] = []
        self._descriptors: Dict[str, TaskTemplateDescriptor] = {}
        self._raw_definitions: Dict[str, Dict[str, Any]] = {}
        self._compiled_templates: Dict[tuple, CompiledTemplate] = {}

    def add_provider(self, provider: ITemplateProvider):
        self._providers.append(provider)

    def load_all(self):
        for provider in self._providers:
            raw_templates = provider.load_templates()
            for raw in raw_templates:
                try:
                    self._validate_schema(raw)
                    desc = self._create_descriptor(raw)
                    self._descriptors[desc.id] = desc
                    self._raw_definitions[desc.id] = raw
                    self._logger.info(f"Loaded template descriptor: {desc.id} (v{desc.version})")
                except Exception as e:
                    self._logger.error(f"Failed to load template: {e}")

    def _validate_schema(self, raw: Dict[str, Any]):
        required_fields = ["id", "version", "schema_version", "goal", "nodes"]
        for field in required_fields:
            if field not in raw:
                raise ValueError(f"Missing required field: {field}")

    def _create_descriptor(self, raw: Dict[str, Any]) -> TaskTemplateDescriptor:
        return TaskTemplateDescriptor(
            id=raw["id"],
            version=str(raw["version"]),
            schema_version=int(raw["schema_version"]),
            goal=raw["goal"],
            summary=raw.get("summary", ""),
            category=raw.get("category", "General"),
            author=raw.get("author", "Unknown"),
            required_inputs=raw.get("required_inputs", {}),
            outputs=raw.get("outputs", {}),
            permissions=raw.get("permissions", []),
            estimated_duration=raw.get("estimated_duration", "Unknown"),
            tags=raw.get("tags", [])
        )

    def get_descriptor(self, template_id: str) -> Optional[TaskTemplateDescriptor]:
        return self._descriptors.get(template_id)

    def _generate_uuid(self, template_id: str, version: str, node_id: str) -> str:
        import hashlib
        return hashlib.sha256(f"{template_id}:{version}:{node_id}".encode()).hexdigest()[:12]

    def compile_template(self, template_id: str) -> CompiledTemplate:
        """Rule 71 & 72 & 75: Compile into an immutable graph before execution and cache it."""
        desc = self.get_descriptor(template_id)
        if not desc:
            raise ValueError(f"Template {template_id} not found.")

        cache_key = (desc.id, desc.version, desc.schema_version)
        if cache_key in self._compiled_templates:
            return self._compiled_templates[cache_key]

        raw = self._raw_definitions[template_id]
        
        nodes: Dict[str, TemplateNode] = {}
        entry_node_uuid = None
        
        raw_nodes = raw.get("nodes", [])
        if not raw_nodes:
            raise ValueError("Template has no nodes.")
            
        # First pass: map node IDs to UUIDs
        id_to_uuid = {}
        for n in raw_nodes:
            id_to_uuid[n["id"]] = self._generate_uuid(desc.id, desc.version, n["id"])

        for i, n in enumerate(raw_nodes):
            node_id = n["id"]
            node_uuid = id_to_uuid[node_id]
            if i == 0:
                entry_node_uuid = node_uuid
                
            next_id = n.get("next")
            next_uuid = id_to_uuid[next_id] if next_id in id_to_uuid else None
                
            nodes[node_uuid] = TemplateNode(
                id=node_id,
                uuid=node_uuid,
                action=n.get("action"),
                type=n.get("type", "capability"),
                message=n.get("message"),
                permissions=n.get("permissions", []),
                next=next_uuid,
                parameters=n.get("parameters", {}),
                outputs=n.get("outputs", {}),
                retry_policy=n.get("retry_policy")
            )
            
        compiled = CompiledTemplate(
            descriptor=desc,
            nodes=nodes,
            entry_node_id=entry_node_uuid,
            conditions=raw.get("conditions", {}),
            metadata=raw.get("metadata", {})
        )
        self._compiled_templates[cache_key] = compiled
        return compiled

    def instantiate(self, template_id: str, parameters: Dict[str, Any]) -> TemplateContext:
        """Creates the runtime context for the template execution."""
        desc = self.get_descriptor(template_id)
        if not desc:
            raise ValueError(f"Template {template_id} not found.")
            
        for req in desc.required_inputs:
            if req not in parameters:
                raise ValueError(f"Missing required parameter: {req}")
                
        compiled = self.compile_template(template_id)
        
        from desktop.platform.shared.models.template import ExecutionCursor
        return TemplateContext(
            template_id=template_id,
            version=desc.version,
            parameters=parameters,
            compiled_nodes=compiled.nodes,
            cursor=ExecutionCursor(current_node_uuid=compiled.entry_node_id)
        )
