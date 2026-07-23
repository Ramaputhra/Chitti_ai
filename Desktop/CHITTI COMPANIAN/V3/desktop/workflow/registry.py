import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from desktop.workflow.models import WorkflowTemplate
from desktop.models.cognition import ExecutionPlan, WorkflowRequest

class WorkflowTemplateRegistry:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.workflows_dir = self.config_dir / "workflows"
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
    def load(self):
        self.templates.clear()
        if not self.workflows_dir.exists():
            return
            
        for filepath in self.workflows_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    template = WorkflowTemplate(
                        workflow_id=data.get("workflow_id", filepath.stem),
                        version=data.get("version", 1),
                        steps=data.get("steps", []),
                        name=data.get("name", filepath.stem),
                        description=data.get("description", ""),
                        category=data.get("category", "general"),
                        tags=data.get("tags", []),
                        created_at=data.get("created_at", time.time()),
                        modified_at=data.get("modified_at", time.time()),
                        last_executed=data.get("last_executed", 0.0),
                        execution_count=data.get("execution_count", 0),
                        estimated_duration_sec=data.get("estimated_duration_sec", 0.0)
                    )
                    self.templates[template.workflow_id] = template
            except Exception as e:
                pass
                
    def get_template(self, workflow_id: str) -> Optional[WorkflowTemplate]:
        return self.templates.get(workflow_id)

    def list_templates(self) -> List[WorkflowTemplate]:
        return list(self.templates.values())


    def save_template(self, template: WorkflowTemplate) -> bool:
        try:
            self.workflows_dir.mkdir(parents=True, exist_ok=True)
            filepath = self.workflows_dir / f"{template.workflow_id}.json"
            
            data = {
                "workflow_id": template.workflow_id,
                "version": template.version,
                "steps": template.steps,
                "name": template.name or template.workflow_id,
                "description": template.description,
                "category": template.category,
                "tags": template.tags,
                "created_at": template.created_at or time.time(),
                "modified_at": time.time(),
                "last_executed": template.last_executed,
                "execution_count": template.execution_count,
                "estimated_duration_sec": template.estimated_duration_sec
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            self.templates[template.workflow_id] = template
            return True
        except Exception:
            return False

    def delete_template(self, workflow_id: str) -> bool:
        if workflow_id in self.templates:
            filepath = self.workflows_dir / f"{workflow_id}.json"
            if filepath.exists():
                try:
                    filepath.unlink()
                except Exception:
                    pass
            del self.templates[workflow_id]
            return True
        return False

    def rename_template(self, workflow_id: str, new_name: str) -> bool:
        template = self.get_template(workflow_id)
        if template:
            template.name = new_name
            return self.save_template(template)
        return False

    def search_templates(self, query: str = "", category: Optional[str] = None) -> List[WorkflowTemplate]:
        results = []
        q_lower = query.lower()
        for t in self.templates.values():
            if category and t.category.lower() != category.lower():
                continue
            if not query or q_lower in t.workflow_id.lower() or q_lower in t.name.lower() or q_lower in t.description.lower() or any(q_lower in tag.lower() for tag in t.tags):
                results.append(t)
        return results

    def save_plan_as_template(self, plan: ExecutionPlan, workflow_id: str, name: str = "", description: str = "", category: str = "custom") -> WorkflowTemplate:
        steps_data = []
        for wf in getattr(plan, "workflows", []):
            steps_data.append({
                "action": getattr(wf, "action", ""),
                "correlation_id": getattr(wf, "correlation_id", ""),
                "parameters": getattr(wf, "parameters", {}) or {}
            })
            
        template = WorkflowTemplate(
            workflow_id=workflow_id,
            version=1,
            steps=steps_data,
            name=name or workflow_id,
            description=description,
            category=category,
            created_at=time.time(),
            modified_at=time.time()
        )
        self.save_template(template)
        return template

