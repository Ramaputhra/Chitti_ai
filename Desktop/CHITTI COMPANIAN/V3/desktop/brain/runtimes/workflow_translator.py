from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from desktop.models.transformations import (
    TransformationContract, ValidationResult, PreconditionsFailure, OutputValidationFailure
)
from desktop.models.planning import Plan, PlanStep
from desktop.models.workflow import Workflow, WorkflowTask, ParameterBinding, TransitionCondition

# Stubbing Capability model representing a registered Capability
@dataclass(frozen=True)
class CapabilitySchema:
    parameters: Dict[str, type] # e.g. {"query": str, "max_results": int}
    returns: type

@dataclass(frozen=True)
class CapabilityDefinition:
    capability_id: str
    version: str
    supported_intents: List[str]
    input_schema: CapabilitySchema
    output_schema: CapabilitySchema
    required_permissions: List[str]
    is_deprecated: bool

class CapabilityRegistry:
    """Catalog of available platform capabilities and their schemas."""
    def find_capability_for_intent(self, intent: str, require_exact: bool = True) -> Optional[CapabilityDefinition]:
        # Deterministically matches intent to CapabilityDefinition
        return None
        
    def get_capability(self, capability_id: str) -> Optional[CapabilityDefinition]:
        return None

@dataclass(frozen=True)
class TranslationPolicy:
    """Governs translation behavior, not capability selection."""
    fail_fast_on_missing: bool = True
    allow_deprecated_capabilities: bool = False
    require_strict_schema_match: bool = True
    prefer_newer_versions: bool = True

class WorkflowTranslator(TransformationContract[Plan, Workflow]):
    """
    Transforms a Plan into an executable Workflow.
    Strictly a binding engine. Does not retrieve data or execute side effects.
    """
    def __init__(self, registry: CapabilityRegistry, policy: TranslationPolicy):
        self.registry = registry
        self.policy = policy

    @property
    def runtime_name(self) -> str:
        return "WorkflowTranslator"

    def validate_input(self, input_data: Plan) -> ValidationResult:
        errors = []
        if not input_data.steps:
            errors.append("Plan contains no steps to translate.")
        if not input_data.plan_id:
            errors.append("Plan missing plan_id.")
        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def transform(self, input_data: Plan) -> Workflow:
        tasks = []
        import uuid
        
        # We will build WorkflowTasks corresponding to PlanSteps
        # Very simplified mock transformation
        for step in input_data.steps:
            # 1. Contract Matching
            cap_def = self.registry.find_capability_for_intent(step.action_intent)
            
            if not cap_def:
                if self.policy.fail_fast_on_missing:
                    # RULE: Fail translation immediately. Do not generate a broken workflow.
                    raise PreconditionsFailure(f"No available capability to satisfy intent: '{step.action_intent}'")
                else:
                    # In a highly permissive policy, we might still fail if there's strictly no fallback
                    raise PreconditionsFailure(f"Capability resolution failed for intent: '{step.action_intent}'")
                    
            if cap_def.is_deprecated and not self.policy.allow_deprecated_capabilities:
                raise PreconditionsFailure(f"Capability '{cap_def.capability_id}' is deprecated and policy forbids it.")
            
            # 2. Binding Generation (Abstract -> Concrete)
            bindings = [] # In reality, we'd map step parameters to ParameterBinding objects
            
            task = WorkflowTask(
                task_id=str(uuid.uuid4()),
                capability_id=cap_def.capability_id,
                bindings=bindings,
                transitions=[] # In reality, mapped from PlanDependency
            )
            tasks.append(task)
            
        workflow = Workflow(
            workflow_id=str(uuid.uuid4()),
            plan_id=input_data.plan_id,
            tasks=tasks
        )
        
        return workflow

    def validate_output(self, output_data: Workflow) -> ValidationResult:
        errors = []
        warnings = []
        
        # Check Rule 238: Workflows Must Be Fully Bound
        for task in output_data.tasks:
            cap_def = self.registry.get_capability(task.capability_id)
            if not cap_def:
                errors.append(f"Task {task.task_id} references unknown capability {task.capability_id}")
                continue
                
            # Schema Compatibility Check
            # Validate that the bound inputs match the expected capability schema
            bound_keys = {b.parameter for b in task.bindings}
            required_keys = set(cap_def.input_schema.parameters.keys())
            
            missing = required_keys - bound_keys
            if missing:
                errors.append(f"Task {task.task_id} is missing required bindings: {missing}")
                
            # Here we would also validate type compatibility of the sources (e.g. Image -> Text)
                
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
