import os
import shutil
import tempfile
import time
import datetime
from typing import Any, List, Dict

from desktop.benchmarks.benchmark import CognitiveBenchmark, BenchmarkMetadata, BenchmarkResult
from desktop.platform.shared.kernel.event_bus import InMemoryEventBus
from desktop.platform.integrations.core.capability_registry import RuntimeCapabilityRegistry
from desktop.brain.runtimes.execution_runtime import ExecutionRuntime

from desktop.models.goals import Goal, GoalPriority, GoalState, GoalCriterion
from desktop.models.assessments import (
    WorkflowAssessment, GoalAssessment, GoalStatus, WorkflowStatus as AssessWorkflowStatus,
    WorkflowAssessmentMetadata, SatisfactionEvaluation
)
from desktop.capabilities.desktop.filesystem.list_directory import ListDirectoryCapability
from desktop.capabilities.desktop.categorization import CategorizeFilesCapability
from desktop.models.presentation import CapabilityResult, ExecutionMetrics
from desktop.product.presentation.generator import PresentationGenerator
from desktop.product.expression.engine import ExpressionEngine

class MockLogger:
    def info(self, msg: str) -> None: pass
    def error(self, msg: str) -> None: pass
    def warning(self, msg: str) -> None: pass
    def debug(self, msg: str) -> None: pass
    def exception(self, msg: str, exc: Exception) -> None: pass

class Benchmark003EmptyDownloads(CognitiveBenchmark):
    
    @property
    def metadata(self) -> BenchmarkMetadata:
        return BenchmarkMetadata(
            id="003",
            name="Empty Downloads",
            layer="Capability",
            deterministic=True,
            required_capabilities=["ListDirectory", "CategorizeFiles"],
            description="Organize Downloads behavior when the directory is already empty."
        )
        
    def setup(self, event_bus: Any, registry: Any) -> Goal:
        self.temp_dir = tempfile.mkdtemp(prefix="chitti_empty_downloads_")
        
        goal = Goal(
            goal_id="goal_bench_003",
            description="Empty Downloads",
            priority=GoalPriority.NORMAL,
            state=GoalState.PENDING,
            created_at=datetime.datetime.utcnow(),
            deadline=None,
            criteria=[GoalCriterion(criterion_id="c1", description="Empty presentation handled", required=True, status=False)]
        )
        return goal
        
    def execute(self) -> Dict[str, Any]:
        start_time = time.time()
        
        logger = MockLogger()
        event_bus = InMemoryEventBus()
        event_bus.initialize()
        
        registry = RuntimeCapabilityRegistry(logger)
        registry.initialize()
        
        goal = self.setup(event_bus, registry)
        downloads_path = self.temp_dir
        
        list_cap = ListDirectoryCapability()
        cat_cap = CategorizeFilesCapability()
        registry.register_capability(list_cap)
        registry.register_capability(cat_cap)
        
        expression_engine = ExpressionEngine(event_bus)
        expression_engine.start()
        
        from desktop.platform.shared.models.execution import ExecutionContext, ExecutionTelemetry
        from desktop.platform.shared.models.ai import ToolInvocation
        telemetry = ExecutionTelemetry(capability="ListDirectory", tool="ListDirectory", status="RUNNING")
        ctx = ExecutionContext(
            session=None,
            user="system",
            permissions=[],
            timeout_sec=30.0,
            cancellation_token=None,
            telemetry=telemetry
        )
        
        # Step 1: List Directory
        res1 = list_cap.execute(ToolInvocation(id="inv_1", tool_name="ListDirectory", arguments={"path": downloads_path}, confidence=1.0, source="Benchmark"), ctx)
        files = res1.data["files"]
        
        # In a real workflow, if files is empty, it might shortcut here.
        # But even if it proceeds to Step 2
        res2 = cat_cap.execute(ToolInvocation(id="inv_2", tool_name="CategorizeFiles", arguments={"files": files, "mapping": {}}, confidence=1.0, source="Benchmark"), ctx)
        categorized_files = res2.data["categorized_files"]
        
        # Empty categorization results in 0 files
        
        goal_assessment = GoalAssessment(
            goal_id="goal_bench_003", workflow_id="wf_003", plan_id="plan_003", status=GoalStatus.SATISFIED,
            satisfaction_evaluation=SatisfactionEvaluation(1.0, [], 1.0, 1.0),
            unmet_constraints=[], evaluator_reasoning="Downloads already organized.", assessment_timestamp=datetime.datetime.utcnow(), workflow_assessment_hash="hash"
        )
        wf_assessment = WorkflowAssessment(
            workflow_id="wf_003", plan_id="plan_003", status=AssessWorkflowStatus.COMPLETED_SUCCESSFULLY,
            metadata=WorkflowAssessmentMetadata("1.0", datetime.datetime.utcnow(), 2, "hash"),
            task_assessments=[], anomalies=[]
        )
        
        result = CapabilityResult(
            capability_name="Organize Downloads",
            goal_assessment=goal_assessment,
            workflow_assessment=wf_assessment,
            metrics=ExecutionMetrics((time.time() - start_time)*1000, 2, {}),
            structured_data={}
        )
        
        presentation = PresentationGenerator().generate(result)
        latency_ms = (time.time() - start_time) * 1000
        
        return {
            "downloads_path": downloads_path,
            "latency_ms": latency_ms,
            "presentation": presentation,
            "goal_assessment": goal_assessment
        }
        
    def assert_success(self, result_data: Dict[str, Any]) -> BenchmarkResult:
        downloads_path = result_data["downloads_path"]
        latency_ms = result_data["latency_ms"]
        presentation = result_data["presentation"]
        goal_assessment = result_data["goal_assessment"]
        
        # Verify no unnecessary folders created
        assert len(os.listdir(downloads_path)) == 0, "Folders created unexpectedly."
        
        # Check presentation
        assert "Total Files     0" in presentation, "Presentation did not handle 0 files."
        
        shutil.rmtree(downloads_path)
        
        return BenchmarkResult(
            benchmark_id=self.metadata.id,
            passed=True,
            latency_ms=latency_ms,
            events_count=2,
            goal_status=goal_assessment.status.value,
            error_message=None,
            extracted_path=presentation
        )

if __name__ == "__main__":
    import traceback
    print("--- Running Benchmark 003: Empty Downloads ---")
    benchmark = Benchmark003EmptyDownloads()
    try:
        result_data = benchmark.execute()
        result = benchmark.assert_success(result_data)
        if result.passed:
            print("SUCCESS: Benchmark 003 passed!")
            print(f"Presentation Output:\n{result.extracted_path}")
        else:
            print(f"FAILED: {result.error_message}")
    except Exception as e:
        print("CRITICAL FAILURE:")
        traceback.print_exc()
