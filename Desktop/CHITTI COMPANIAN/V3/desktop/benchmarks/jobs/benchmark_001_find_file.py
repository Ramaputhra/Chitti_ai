import datetime
import time
from typing import Any, List, Dict

from desktop.benchmarks.benchmark import CognitiveBenchmark, BenchmarkMetadata, BenchmarkResult
from desktop.platform.shared.kernel.event_bus import InMemoryEventBus
from desktop.platform.integrations.core.capability_registry import RuntimeCapabilityRegistry
from desktop.brain.runtimes.execution_runtime import ExecutionRuntime

from desktop.models.goals import Goal, GoalPriority, GoalState, GoalCriterion
from desktop.models.assessments import GoalStatus

# We import the stubs that were created in the walking skeleton.
# To keep this self-contained, we can define them here or import from app if we moved them.
# For now, defining them here as this benchmark defines the deterministic skeleton for 'Find File'.
from desktop.app.test_end_to_end_spine import (
    FilesystemCapability,
    GoalContextBuilderStub,
    PlannerRuntimeStub,
    WorkflowTranslatorStub,
    WorkflowEvaluatorStub,
    GoalEvaluatorStub,
    MockLogger
)


class Benchmark001FindFile(CognitiveBenchmark):
    
    @property
    def metadata(self) -> BenchmarkMetadata:
        return BenchmarkMetadata(
            id="001",
            name="Find File",
            layer="Bring-up",
            deterministic=True,
            required_capabilities=["FilesystemCapability"],
            description="Find ABCD.pdf through the entire deterministic cognitive spine."
        )
        
    def setup(self, event_bus: Any, registry: Any) -> Goal:
        registry.register_capability(FilesystemCapability())
        
        goal = Goal(
            goal_id="goal_bench_001",
            description="Find ABCD.pdf",
            priority=GoalPriority.NORMAL,
            state=GoalState.PENDING,
            created_at=datetime.datetime.utcnow(),
            deadline=None,
            criteria=[
                GoalCriterion(criterion_id="c1", description="Returns absolute path to ABCD.pdf", required=True, status=False)
            ]
        )
        return goal
        
    def execute(self) -> Dict[str, Any]:
        """Exercises the entire cognitive spine deterministically."""
        start_time = time.time()
        
        logger = MockLogger()
        event_bus = InMemoryEventBus()
        event_bus.initialize()
        registry = RuntimeCapabilityRegistry(logger)
        registry.initialize()
        
        goal = self.setup(event_bus, registry)
        
        events = []
        def on_event(event):
            events.append(event.payload.get("event"))
        event_bus.subscribe_all(on_event)

        # Spine Execution
        context = GoalContextBuilderStub().build(goal)
        plan = PlannerRuntimeStub().plan(context)
        workflow = WorkflowTranslatorStub().translate(plan)
        
        ExecutionRuntime(registry, event_bus).execute_workflow(workflow)
        
        wf_assessment = WorkflowEvaluatorStub().evaluate(workflow.workflow_id, events)
        goal_assessment = GoalEvaluatorStub().evaluate(goal, wf_assessment)
        
        latency_ms = (time.time() - start_time) * 1000
        
        return {
            "events": events,
            "goal_assessment": goal_assessment,
            "wf_assessment": wf_assessment,
            "latency_ms": latency_ms
        }
        
    def assert_success(self, result_data: Dict[str, Any]) -> BenchmarkResult:
        events = result_data["events"]
        goal_assessment = result_data["goal_assessment"]
        wf_assessment = result_data["wf_assessment"]
        latency_ms = result_data["latency_ms"]
        
        event_names = [e.__class__.__name__ for e in events]
        passed = all([
            "TaskStartedEvent" in event_names,
            "TaskCompletedEvent" in event_names,
            "WorkflowCompletedEvent" in event_names,
            goal_assessment.status == GoalStatus.SATISFIED
        ])
        
        extracted_path = wf_assessment.task_assessments[0].extracted_outputs.get("summary", "") if wf_assessment.task_assessments else None
        
        return BenchmarkResult(
            benchmark_id=self.metadata.id,
            passed=passed,
            latency_ms=latency_ms,
            events_count=len(events),
            goal_status=goal_assessment.status.value,
            error_message=None if passed else "Spine assertions failed.",
            extracted_path=extracted_path
        )
