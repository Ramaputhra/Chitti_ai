from dataclasses import dataclass
from desktop.models.transformations import TransformationContract, ValidationResult
from desktop.models.goals import Goal
from desktop.models.assessments import WorkflowAssessment, GoalAssessment

@dataclass(frozen=True)
class GoalEvaluationContext:
    """The immutable input contract for Goal Evaluation."""
    goal: Goal
    workflow_assessment: WorkflowAssessment

class GoalEvaluator(TransformationContract[GoalEvaluationContext, GoalAssessment]):
    """
    Evaluates execution reality (WorkflowAssessment) against intended intent (GoalCriteria).
    This is the ONLY component authorized to declare goal satisfaction.
    """
    
    @property
    def runtime_name(self) -> str:
        return "GoalEvaluator"

    def validate_input(self, input_data: GoalEvaluationContext) -> ValidationResult:
        errors = []
        if input_data.workflow_assessment.plan_id == "":
            errors.append("WorkflowAssessment missing plan_id, cannot correlate to Goal.")
        # In reality, verify plan_id maps to goal.goal_id
        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def transform(self, input_data: GoalEvaluationContext) -> GoalAssessment:
        from desktop.models.assessments import GoalStatus, SatisfactionEvaluation
        from datetime import datetime
        
        # 1. Iterate over input_data.goal.success_criteria
        # 2. For each GoalCriterion:
        #    a) If deterministic, evaluate algorithmic rules against WorkflowAssessment
        #    b) If semantic, optionally dispatch to LLM bounded evaluator
        # 3. Aggregate results into SatisfactionEvaluation
        
        # Simplified Mock Output
        eval_result = SatisfactionEvaluation(
            score=1.0,
            contributing_criteria=["criterion_1_deterministic", "criterion_2_semantic"],
            semantic_confidence=0.92,
            deterministic_score=1.0
        )
        
        return GoalAssessment(
            goal_id=input_data.goal.goal_id,
            workflow_id=input_data.workflow_assessment.workflow_id,
            plan_id=input_data.workflow_assessment.plan_id,
            status=GoalStatus.SATISFIED,
            satisfaction_evaluation=eval_result,
            unmet_constraints=[],
            evaluator_reasoning="All deterministic and semantic criteria were fully met.",
            assessment_timestamp=datetime.utcnow(),
            workflow_assessment_hash=input_data.workflow_assessment.metadata.execution_history_hash
        )

    def validate_output(self, output_data: GoalAssessment) -> ValidationResult:
        errors = []
        if not output_data.workflow_assessment_hash:
            errors.append("GoalAssessment missing workflow_assessment_hash.")
        return ValidationResult(valid=len(errors) == 0, errors=errors)
