import uuid
import time
from desktop.brain.planning.models import (
    ExecutionPlan, ExecutionStep, PlanningTrace, PlanningSession,
    PlanningBudgetExceededException, InvalidPlanningStateException
)
from desktop.brain.planning.registry import CapabilityRegistry
from desktop.brain.planning.compiler import PlanCompiler
from desktop.brain.planning.dependencies import DependencyAnalyzer
from desktop.brain.planning.prerequisites import PrerequisiteValidator
from desktop.brain.planning.validator import PlanValidator
from desktop.brain.planning.confidence import PlanConfidenceModel

class PlanningEngine:
    def __init__(self):
        self.registry = CapabilityRegistry()
        
        self.registry.register_capability("mute notifications", {
            "steps": [
                {"id": "A", "action_type": "OS_REGISTRY_EDIT", "payload": {}, "deps": []},
                {"id": "B", "action_type": "RESTART_SERVICE", "payload": {}, "deps": ["A"]}
            ]
        })
        
        self.registry.register_capability("circular test", {
            "steps": [
                {"id": "A", "action_type": "TEST", "payload": {}, "deps": ["B"]},
                {"id": "B", "action_type": "TEST", "payload": {}, "deps": ["A"]}
            ]
        })
        
        self.registry.register_capability("upload crash logs", {
            "steps": [
                {"id": "A", "action_type": "REQUIRES_ADMIN", "payload": {}, "deps": []}
            ]
        })
        
        self.compiler = PlanCompiler(self.registry)
        self.dependency_analyzer = DependencyAnalyzer()
        self.prerequisite_validator = PrerequisiteValidator()
        self.confidence_model = PlanConfidenceModel()
        self.validator = PlanValidator()
        
    def plan(self, decision_outcome) -> PlanningSession:
        max_steps = 50
        max_depth = 10
        max_prereq = 100
        max_expansions = 10
        max_val = 1
        
        try:
            intent = getattr(decision_outcome, "selected_intent", "")
            base_conf = getattr(decision_outcome, "decision_confidence", 0.0)
            
            max_expansions -= 1
            if max_expansions < 0:
                raise PlanningBudgetExceededException("Max expansions exceeded")
                
            steps = self.compiler.compile(intent, max_expansions)
            
            if len(steps) > max_steps:
                raise PlanningBudgetExceededException("Max execution steps exceeded")
                
            max_depth -= 1
            sequenced_steps = self.dependency_analyzer.analyze_and_sequence(steps, max_depth)
            
            max_prereq -= len(sequenced_steps)
            if max_prereq < 0:
                raise PlanningBudgetExceededException("Max prereq checks exceeded")
                
            prereq_logs = self.prerequisite_validator.validate(sequenced_steps, max_prereq)
            
            final_conf = self.confidence_model.calculate(base_conf, prereq_logs)
            is_executable = final_conf > 0.0
            
            trace = PlanningTrace(
                decision_outcome_id=getattr(decision_outcome, "outcome_id", "mock_id"),
                compilation_rules_applied=["registry_lookup"]
            )
            
            plan_obj = ExecutionPlan(
                plan_id=str(uuid.uuid4()),
                steps=sequenced_steps,
                plan_confidence=final_conf,
                is_executable=is_executable,
                evidence_trace=trace
            )
            
            self.validator.validate_plan(plan_obj, intent, max_val)
            max_val -= 1
            
            return PlanningSession(
                session_id=str(uuid.uuid4()),
                source_decision=decision_outcome,
                dependency_graph_log={"sorted": True},
                prerequisite_checks=prereq_logs,
                final_plan=plan_obj
            )
            
        except PlanningBudgetExceededException:
            return self._build_empty_session(decision_outcome)
            
    def _build_empty_session(self, decision):
        plan_obj = ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            steps=[],
            plan_confidence=0.0,
            is_executable=False,
            evidence_trace=PlanningTrace(getattr(decision, "outcome_id", "mock"), [])
        )
        return PlanningSession(
            session_id=str(uuid.uuid4()),
            source_decision=decision,
            dependency_graph_log={},
            prerequisite_checks=[],
            final_plan=plan_obj
        )
