from typing import List, Dict, Any, Optional
import uuid
from desktop.models.service_registry import ServiceDescriptor
from desktop.models.composer import CompositionPolicy, ServiceChain, WorkflowBlueprint, WorkflowNode
from desktop.models.reasoning import ReasoningPlan
from desktop.models.retrieval import ContextPackage

class DeterministicComposer:
    """
    Rule 304: Deterministic Composition.
    Implements a linear O(n) walk to chain capabilities based on accepts/produces metadata.
    """
    def __init__(self, service_registry):
        self.service_registry = service_registry

    def compose(self, plan: ReasoningPlan, context: ContextPackage, policy: CompositionPolicy) -> WorkflowBlueprint:
        blueprint = WorkflowBlueprint(
            blueprint_id=f"wp_{uuid.uuid4().hex[:8]}",
            intent="dynamic_composition"
        )
        
        # In a real implementation, we would extract the target outputs from the intent/plan.
        # Here we simulate building a linear chain based on the required capabilities.
        
        candidates = self._gather_candidates(plan)
        if not candidates:
            return blueprint
            
        # Sort candidates according to the policy (e.g., fastest, offline-first)
        sorted_candidates = self._score_and_sort(candidates, policy)
        
        # Build the chain
        chain = self._build_linear_chain(sorted_candidates)
        
        # Convert the ServiceChain into a WorkflowBlueprint (DAG representation)
        self._chain_to_blueprint(chain, blueprint)
        
        return blueprint

    def _gather_candidates(self, plan: ReasoningPlan) -> List[ServiceDescriptor]:
        # Stub: fetch all services from registry that match required capabilities
        # (e.g., if plan.requires_presentation is True, fetch presentation templates)
        return []

    def _score_and_sort(self, candidates: List[ServiceDescriptor], policy: CompositionPolicy) -> List[ServiceDescriptor]:
        if policy == CompositionPolicy.FASTEST:
            return sorted(candidates, key=lambda s: s.latency_ms)
        elif policy == CompositionPolicy.OFFLINE_FIRST:
            return sorted(candidates, key=lambda s: (not s.offline_capable, s.priority))
        else: # STRICT / Default
            return sorted(candidates, key=lambda s: (-s.priority, s.latency_ms))

    def _build_linear_chain(self, sorted_candidates: List[ServiceDescriptor]) -> ServiceChain:
        chain = ServiceChain(input_type="raw_intent", output_type="unknown")
        
        # O(n) walk to find matching outputs to inputs
        # For this stub, we just append them linearly.
        # In full implementation: Check `produces` of step N against `accepts` of step N+1.
        for service in sorted_candidates:
            chain.steps.append(service)
            
        return chain
        
    def _chain_to_blueprint(self, chain: ServiceChain, blueprint: WorkflowBlueprint):
        prev_node_id = None
        for i, service in enumerate(chain.steps):
            node_id = f"node_{i}"
            node = WorkflowNode(
                node_id=node_id,
                service_id=service.id,
                dependencies=[prev_node_id] if prev_node_id else []
            )
            blueprint.nodes[node_id] = node
            prev_node_id = node_id
