from dataclasses import dataclass
from typing import List
from desktop.models.transformations import TransformationContract, ValidationResult
from desktop.models.assessments import GoalAssessment
from desktop.models.execution_events import ExecutionEvent
from desktop.models.memory import ConsolidationReport

@dataclass(frozen=True)
class ConsolidationContext:
    """The immutable input contract for Memory Consolidation."""
    goal_assessment: GoalAssessment
    events: List[ExecutionEvent]

class MemoryConsolidator(TransformationContract[ConsolidationContext, ConsolidationReport]):
    """
    Transforms raw execution events into explicit Knowledge and Heuristic Records.
    Requires a completed GoalAssessment to ensure we don't learn hallucinations.
    Does not write directly to DB.
    """
    
    @property
    def runtime_name(self) -> str:
        return "MemoryConsolidator"

    def validate_input(self, input_data: ConsolidationContext) -> ValidationResult:
        errors = []
        if input_data.goal_assessment.workflow_id != input_data.events[0].workflow_id:
            errors.append("GoalAssessment workflow ID does not match the provided ExecutionEvents.")
        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def transform(self, input_data: ConsolidationContext) -> ConsolidationReport:
        from desktop.models.memory import ExtractionMetadata
        from datetime import datetime
        
        # 1. Use input_data.goal_assessment to decide if the workflow outputs are valid
        # 2. Extract facts into KnowledgeRecords (Declarative Learning)
        # 3. Extract strategy/performance into HeuristicRecords (Procedural Learning)
        # 4. Filter out useless data
        
        metadata = ExtractionMetadata(
            extractor_version="1.0.0",
            extraction_timestamp=datetime.utcnow()
        )
        
        return ConsolidationReport(
            workflow_id=input_data.goal_assessment.workflow_id,
            plan_id=input_data.goal_assessment.plan_id,
            knowledge_records=[],
            heuristic_records=[],
            ignored_facts=[],
            extraction_metadata=metadata
        )

    def validate_output(self, output_data: ConsolidationReport) -> ValidationResult:
        errors = []
        # Validate that provenance fields in records map back to the input context
        return ValidationResult(valid=len(errors) == 0, errors=errors)
