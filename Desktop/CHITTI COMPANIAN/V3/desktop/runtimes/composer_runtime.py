from desktop.models.reasoning import ReasoningPlan
from desktop.models.retrieval import ContextPackage
from desktop.models.composer import WorkflowBlueprint, CompositionPolicy
from desktop.runtimes.composer.deterministic_composer import DeterministicComposer
from desktop.runtimes.composer.validator import WorkflowValidator
import logging

class ComposerRuntime:
    """
    Rule 300: Composer determines composition based on Service Declarations.
    Rule 304: Deterministic Composition.
    Orchestrates the creation and validation of the WorkflowBlueprint.
    """
    def __init__(self, service_registry=None, event_bus=None):
        self.service_registry = service_registry
        self.event_bus = event_bus
        self.composer = DeterministicComposer(service_registry)
        self.validator = WorkflowValidator()
        self.default_policy = CompositionPolicy.STRICT

    def _emit(self, event_name: str, payload: dict):
        if self.event_bus:
            self.event_bus.publish(event_name, payload)

    def compose_workflow(self, plan: ReasoningPlan, context: ContextPackage, policy: CompositionPolicy = None) -> WorkflowBlueprint:
        """
        The main entrypoint for translating a ReasoningPlan into an executable WorkflowBlueprint.
        """
        active_policy = policy or self.default_policy
        self._emit("CompositionStarted", {"strategy": plan.strategy.value, "policy": active_policy.value})
        
        # 1. Deterministic Composition
        blueprint = self.composer.compose(plan, context, active_policy)
        
        # 2. Validation
        is_valid = self.validator.validate(blueprint)
        
        if not is_valid:
            error_msg = f"Failed to validate composed workflow: {blueprint.validation_trace}"
            logging.error(error_msg)
            self._emit("CompositionFailed", {"blueprint_id": blueprint.blueprint_id, "trace": blueprint.validation_trace})
            # In a full system, this might trigger a fallback to AI Gateway or notify the user.
            raise RuntimeError(error_msg)
            
        self._emit("CompositionCompleted", {"blueprint_id": blueprint.blueprint_id, "nodes_count": len(blueprint.nodes)})
        return blueprint
