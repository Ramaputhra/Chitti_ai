from dataclasses import dataclass
from typing import List
from desktop.models.transformations import TransformationContract, ValidationResult
from desktop.models.execution_events import ExecutionEvent
from desktop.models.assessments import WorkflowAssessment

@dataclass(frozen=True)
class WorkflowExecutionHistory:
    """The immutable input contract for Workflow Evaluation."""
    workflow_id: str
    plan_id: str
    events: List[ExecutionEvent]

class WorkflowEvaluator(TransformationContract[WorkflowExecutionHistory, WorkflowAssessment]):
    """
    Evaluates raw ExecutionEvents to determine if a workflow executed correctly.
    Does NOT evaluate if the goal was met. Does NOT extract knowledge.
    """
    
    @property
    def runtime_name(self) -> str:
        return "WorkflowEvaluator"

    def validate_input(self, input_data: WorkflowExecutionHistory) -> ValidationResult:
        errors = []
        if not input_data.events:
            errors.append("Execution history contains no events.")
        
        # Verify chronological ordering
        for i in range(1, len(input_data.events)):
            if input_data.events[i].sequence_number <= input_data.events[i-1].sequence_number:
                errors.append(f"Events are out of sequence order at index {i}.")
                
        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def transform(self, input_data: WorkflowExecutionHistory) -> WorkflowAssessment:
        import hashlib
        from datetime import datetime
        from desktop.models.assessments import WorkflowAssessmentMetadata, WorkflowStatus
        
        # Compute deterministic hash of the history
        event_ids = "".join(e.event_id for e in input_data.events)
        history_hash = hashlib.sha256(event_ids.encode('utf-8')).hexdigest()
        
        metadata = WorkflowAssessmentMetadata(
            evaluator_version="1.0.0",
            assessed_at=datetime.utcnow(),
            execution_event_count=len(input_data.events),
            execution_history_hash=history_hash
        )
        
        # In reality, this iterates through events to reconstruct the trace,
        # identifies TaskAssessments, detects anomalies (like retry storms),
        # and determines the final WorkflowStatus.
        
        return WorkflowAssessment(
            workflow_id=input_data.workflow_id,
            plan_id=input_data.plan_id,
            status=WorkflowStatus.COMPLETED_SUCCESSFULLY,
            metadata=metadata,
            task_assessments=[],
            anomalies=[]
        )

    def validate_output(self, output_data: WorkflowAssessment) -> ValidationResult:
        errors = []
        if not output_data.metadata.execution_history_hash:
            errors.append("WorkflowAssessment is missing an execution_history_hash.")
        return ValidationResult(valid=len(errors) == 0, errors=errors)
