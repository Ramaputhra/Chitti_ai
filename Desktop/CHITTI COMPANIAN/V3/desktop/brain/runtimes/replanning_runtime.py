from dataclasses import dataclass
from desktop.models.transformations import TransformationContract, ValidationResult
from desktop.models.goals import GoalContext
from desktop.models.assessments import GoalAssessment
from desktop.models.memory import ConsolidationReport
from desktop.models.planning import PlanningContext, ReplanningDirective, ReplanningFailureCategory

@dataclass(frozen=True)
class ReplanningInput:
    """The immutable input contract for Replanning."""
    previous_context: GoalContext
    goal_assessment: GoalAssessment
    consolidation_report: ConsolidationReport

@dataclass(frozen=True)
class ReplanningOutput:
    """The pure transformation output. The orchestration layer handles lifecycle events."""
    planning_context: PlanningContext

class ReplanningRuntime(TransformationContract[ReplanningInput, ReplanningOutput]):
    """
    Transforms failure context into a new PlanningContext with explicit directives.
    Does NOT emit lifecycle events (like GoalAbandonedEvent).
    Does NOT mutate previous plans or history.
    """
    
    @property
    def runtime_name(self) -> str:
        return "ReplanningRuntime"

    def validate_input(self, input_data: ReplanningInput) -> ValidationResult:
        from desktop.models.assessments import GoalStatus
        errors = []
        if input_data.goal_assessment.status == GoalStatus.SATISFIED:
            errors.append("Cannot replan a SATISFIED goal.")
        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def transform(self, input_data: ReplanningInput) -> ReplanningOutput:
        # 1. Check max retries based on goal's lineage
        # 2. Extract specific failure category
        # 3. Formulate ReplanningDirective pulling from HeuristicRecords
        
        # Simplified Mock Implementation
        directive = ReplanningDirective(
            failure_category=ReplanningFailureCategory.CAPABILITY_FAILURE,
            avoid_capability_ids=["SearchWeb"], # Derived from an extracted heuristic
            required_heuristics=[],
            adjusted_constraints=[],
            max_retries_exceeded=False
        )
        
        # Wrap the original unchanged GoalContext with the new directive
        planning_context = PlanningContext(
            goal_context=input_data.previous_context,
            replanning_directive=directive
        )
        
        return ReplanningOutput(planning_context=planning_context)

    def validate_output(self, output_data: ReplanningOutput) -> ValidationResult:
        errors = []
        if output_data.planning_context.replanning_directive is None:
            errors.append("ReplanningOutput must contain a directive.")
        return ValidationResult(valid=len(errors) == 0, errors=errors)
