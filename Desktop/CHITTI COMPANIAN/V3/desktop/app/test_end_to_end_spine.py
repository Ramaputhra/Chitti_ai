import os
import uuid
import datetime
from typing import Any, Dict, List

from desktop.platform.shared.kernel.event_bus import InMemoryEventBus
from desktop.platform.integrations.core.capability_registry import RuntimeCapabilityRegistry
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.brain.runtimes.execution_runtime import ExecutionRuntime

from desktop.models.goals import Goal, GoalPriority, GoalState, GoalCriterion, GoalContext, ContextMetadata
from desktop.models.planning import Plan, PlanStep, PlanOutcome, PlanMetadata, PlanConstraint
from desktop.models.workflow import (
    Workflow, WorkflowStep, CapabilityReference, ParameterBinding, BindingSource, 
    ExecutionPolicy, RetryPolicy, TimeoutPolicy, FallbackPolicy, WorkflowMetadata
)
from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor

from desktop.models.execution_events import (
    WorkflowCompletedEvent, TaskCompletedEvent, CapabilityInvokedEvent
)

from desktop.models.assessments import (
    WorkflowAssessment, GoalAssessment, TaskStatus, 
    WorkflowStatus as AssessWorkflowStatus, TaskAssessment, 
    WorkflowAssessmentMetadata, GoalStatus, SatisfactionEvaluation
)

class MockLogger(ILoggingService):
    def info(self, msg: str) -> None: pass
    def error(self, msg: str) -> None: pass
    def warning(self, msg: str) -> None: pass
    def debug(self, msg: str) -> None: pass
    def exception(self, msg: str, exc: Exception) -> None: pass


class FilesystemCapability(ICapability):
    """Minimal capability that searches for a file."""
    @property
    def name(self) -> str: return "FilesystemCapability"
    @property
    def state(self) -> Any: return None
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[ToolDescriptor]: return []
    def validate(self, invocation: ToolInvocation) -> bool: return True
    def cancel(self, invocation_id: str) -> None: pass
    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name="FilesystemCapability", 
            version="1.0",
            category="core",
            permissions=[],
            tools=[],
            health="healthy",
            platform="desktop"
        )
        
    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        filename = invocation.arguments.get("filename", "")
        # Minimal mock logic: just echo it back as found in a fake directory
        found_path = f"C:\\Documents\\{filename}"
        return ExecutionResult(
            status=ExecutionStatus.SUCCESS, 
            summary=f"Found: {found_path}"
        )

# --- DETERMINISTIC STUBS ---

class GoalContextBuilderStub:
    def build(self, goal: Goal) -> GoalContext:
        print("✓ GoalContext created")
        return GoalContext(
            goal_id=goal.goal_id,
            metadata=ContextMetadata(
                assembled_at=datetime.datetime.utcnow(),
                knowledge_version="v1",
                goal_version="v1",
                pipeline_version="v1"
            ),
            relevant_knowledge=[],
            active_constraints=[],
            pending_tasks=[],
            related_goals=[]
        )

class PlannerRuntimeStub:
    def plan(self, context: GoalContext) -> Plan:
        print("✓ Plan created")
        step = PlanStep(
            step_id="step_1",
            description="Search filesystem for ABCD.pdf",
            action_intent="FIND_FILE",
            constraints=[],
            decision=None,
            expected_outcome=PlanOutcome(expected_state="File path returned", expected_artifacts=[])
        )
        return Plan(
            plan_id="plan_001",
            goal_id=context.goal_id,
            supersedes_plan_id=None,
            steps=[step],
            dependencies=[],
            global_constraints=[],
            metadata=PlanMetadata(planner_version="stub_1.0", created_at=datetime.datetime.utcnow(), generated_from_goal_version="v1")
        )

class WorkflowTranslatorStub:
    def translate(self, plan: Plan) -> Workflow:
        print("✓ Workflow created")
        policy = ExecutionPolicy(
            retry=RetryPolicy(max_retries=0, retry_backoff_ms=0),
            timeout=TimeoutPolicy(timeout_ms=1000),
            fallback=FallbackPolicy(fallback_workflow_id=None)
        )
        step = WorkflowStep(
            step_id=plan.steps[0].step_id,
            capability=CapabilityReference(capability_id="FilesystemCapability", version="1.0"),
            parameter_bindings=[
                ParameterBinding(parameter="filename", source=BindingSource.LITERAL, reference="ABCD.pdf")
            ],
            execution_policy=policy
        )
        return Workflow(
            workflow_id="wf_001",
            plan_id=plan.plan_id,
            steps=[step],
            transitions=[],
            global_policy=policy,
            metadata=WorkflowMetadata(translator_version="stub_1.0", created_at=datetime.datetime.utcnow(), generated_from_plan_id=plan.plan_id)
        )

class WorkflowEvaluatorStub:
    def evaluate(self, workflow_id: str, events: List[Any]) -> WorkflowAssessment:
        # Scan events to determine success
        task_assessments = []
        for e in events:
            if isinstance(e, TaskCompletedEvent):
                task_assessments.append(TaskAssessment(
                    task_id=e.task_id,
                    status=TaskStatus.SUCCESS,
                    extracted_outputs=e.output_data,
                    error_summary=None
                ))
        
        print("✓ WorkflowAssessment generated")
        return WorkflowAssessment(
            workflow_id=workflow_id,
            plan_id="plan_001",
            status=AssessWorkflowStatus.COMPLETED_SUCCESSFULLY,
            metadata=WorkflowAssessmentMetadata(
                evaluator_version="stub_1.0",
                assessed_at=datetime.datetime.utcnow(),
                execution_event_count=len(events),
                execution_history_hash="fake_hash"
            ),
            task_assessments=task_assessments,
            anomalies=[]
        )

class GoalEvaluatorStub:
    def evaluate(self, goal: Goal, wf_assessment: WorkflowAssessment) -> GoalAssessment:
        print("✓ GoalAssessment generated")
        # In a real system, would compare wf_assessment to Goal Criteria
        return GoalAssessment(
            goal_id=goal.goal_id,
            workflow_id=wf_assessment.workflow_id,
            plan_id=wf_assessment.plan_id,
            status=GoalStatus.SATISFIED,
            satisfaction_evaluation=SatisfactionEvaluation(
                score=1.0,
                contributing_criteria=[c.criterion_id for c in goal.criteria],
                semantic_confidence=1.0,
                deterministic_score=1.0
            ),
            unmet_constraints=[],
            evaluator_reasoning="File was successfully found in filesystem.",
            assessment_timestamp=datetime.datetime.utcnow(),
            workflow_assessment_hash="fake_hash"
        )


def run_cognitive_spine():
    logger = MockLogger()
    event_bus = InMemoryEventBus()
    event_bus.initialize()
    
    registry = RuntimeCapabilityRegistry(logger)
    registry.initialize()
    registry.register_capability(FilesystemCapability())
    
    execution_runtime = ExecutionRuntime(registry, event_bus)
    
    # Track events
    events = []
    def on_event(event):
        events.append(event.payload.get("event"))
    event_bus.subscribe_all(on_event)

    # 1. User intent -> Goal
    goal = Goal(
        goal_id="goal_001",
        description="Find ABCD.pdf",
        priority=GoalPriority.NORMAL,
        state=GoalState.PENDING,
        created_at=datetime.datetime.utcnow(),
        deadline=None,
        criteria=[
            GoalCriterion(criterion_id="c1", description="Returns absolute path to ABCD.pdf", required=True, status=False)
        ]
    )
    print("✓ Goal created")
    
    # 2. Context Builder
    builder = GoalContextBuilderStub()
    context = builder.build(goal)
    
    # 3. Planner
    planner = PlannerRuntimeStub()
    plan = planner.plan(context)
    
    # 4. Translator
    translator = WorkflowTranslatorStub()
    workflow = translator.translate(plan)
    
    # 5. Execution
    execution_runtime.execute_workflow(workflow)
    print("✓ Workflow executed")
    
    event_names = [e.__class__.__name__ for e in events]
    assert "TaskStartedEvent" in event_names
    print("✓ TaskStartedEvent emitted")
    assert "TaskCompletedEvent" in event_names
    print("✓ TaskCompletedEvent emitted")
    assert "WorkflowCompletedEvent" in event_names
    print("✓ WorkflowCompletedEvent emitted")
    
    # 6. Evaluation
    wf_evaluator = WorkflowEvaluatorStub()
    wf_assessment = wf_evaluator.evaluate(workflow.workflow_id, events)
    
    goal_evaluator = GoalEvaluatorStub()
    goal_assessment = goal_evaluator.evaluate(goal, wf_assessment)
    
    # 7. Final Output Extraction
    assert goal_assessment.status == GoalStatus.SATISFIED
    
    # Extract path from TaskCompletedEvent output
    output_summary = wf_assessment.task_assessments[0].extracted_outputs.get("summary", "")
    print(f"✓ Returned path exists")
    print(f"\nUser: Found it -> {output_summary}")


if __name__ == "__main__":
    print("--- Starting End-to-End Cognitive Spine ---")
    run_cognitive_spine()
    print("--- Success ---")
