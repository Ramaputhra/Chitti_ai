from desktop.models.goals import GoalContext
from desktop.models.planning import Plan, PlanStep, PlanConstraint, PlanDecision, PlanDependency, PlanOutcome

class PlanningException(Exception):
    """Raised when the planning pipeline fails deterministically."""
    pass

class PlannerContextValidator:
    """Ensures the GoalContext contains sufficient information to attempt planning."""
    def validate(self, context: GoalContext) -> bool:
        # Example validation: Must have a goal_id
        if not context.goal_id:
            raise PlanningException("GoalContext is missing goal_id.")
        return True

class PlannerConstraintAnalyzer:
    """Extracts hard and soft constraints from the Context to bound the step generator."""
    def analyze(self, context: GoalContext) -> list[PlanConstraint]:
        # Transforms dynamic context constraints into PlanConstraints
        return []

class PlannerStepGenerator:
    """
    The pluggable engine (heuristic, LLM, or template-based) that proposes abstract steps.
    Must output purely semantic action intents (Rule 225).
    """
    def generate_steps(self, context: GoalContext, constraints: list[PlanConstraint]) -> list[PlanStep]:
        # Returns abstract steps. If context is missing, might return a step to ask the user.
        return []

class PlannerDependencyResolver:
    """Deterministically links generated steps and builds the PlanDependency graph."""
    def resolve(self, steps: list[PlanStep]) -> list[PlanDependency]:
        return []

class PlanValidator:
    """Final check: Does the generated Plan violate any Constraints or Constitutional Rules?"""
    def validate(self, plan: Plan) -> bool:
        # Fails the pipeline if the Plan is structurally invalid or violates constraints.
        return True

class PlannerRuntime:
    """
    Orchestrates the deterministic transformation of GoalContext -> Plan.
    """
    def __init__(
        self,
        validator: PlannerContextValidator,
        constraint_analyzer: PlannerConstraintAnalyzer,
        step_generator: PlannerStepGenerator,
        dependency_resolver: PlannerDependencyResolver,
        plan_validator: PlanValidator
    ):
        self.context_validator = validator
        self.constraint_analyzer = constraint_analyzer
        self.step_generator = step_generator
        self.dependency_resolver = dependency_resolver
        self.plan_validator = plan_validator

    def generate_plan(self, context: GoalContext, previous_plan_id: str = None) -> Plan:
        """
        Executes the deterministic planning pipeline.
        """
        # 1. Validation
        self.context_validator.validate(context)
        
        # 2. Constraint Analysis
        constraints = self.constraint_analyzer.analyze(context)
        
        # 3. Step Generation
        steps = self.step_generator.generate_steps(context, constraints)
        
        # 4. Dependency Resolution
        dependencies = self.dependency_resolver.resolve(steps)
        
        # Assemble draft Plan
        import uuid
        from datetime import datetime
        from desktop.models.planning import PlanStatus, PlanMetadata
        
        metadata = PlanMetadata(
            planner_version="1.0.0",
            created_at=datetime.utcnow(),
            generated_from_goal_version=context.metadata.goal_version if hasattr(context, 'metadata') else "unknown"
        )
        
        draft_plan = Plan(
            plan_id=str(uuid.uuid4()),
            goal_id=context.goal_id,
            supersedes_plan_id=previous_plan_id,
            steps=steps,
            dependencies=dependencies,
            global_constraints=constraints,
            metadata=metadata
        )
        
        # 5. Plan Validation
        self.plan_validator.validate(draft_plan)
        
        return draft_plan
