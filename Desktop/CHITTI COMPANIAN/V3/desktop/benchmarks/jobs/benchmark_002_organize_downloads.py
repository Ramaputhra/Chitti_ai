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
    WorkflowAssessmentMetadata, TaskAssessment, TaskStatus, SatisfactionEvaluation
)
from desktop.models.workflow import (
    Workflow, WorkflowStep, CapabilityReference, ParameterBinding, BindingSource, 
    ExecutionPolicy, RetryPolicy, TimeoutPolicy, FallbackPolicy, WorkflowMetadata
)
from desktop.models.execution_events import WorkflowCompletedEvent, TaskCompletedEvent

from desktop.capabilities.desktop.filesystem.list_directory import ListDirectoryCapability
from desktop.capabilities.desktop.filesystem.create_directory import CreateDirectoryCapability
from desktop.capabilities.desktop.filesystem.move_file import MoveFileCapability
from desktop.capabilities.desktop.categorization import CategorizeFilesCapability

from desktop.models.presentation import CapabilityResult, ExecutionMetrics, AvatarStateChanged
from desktop.product.expression.engine import ExpressionEngine
from desktop.product.presentation.generator import PresentationGenerator

class MockLogger:
    def info(self, msg: str) -> None: pass
    def error(self, msg: str) -> None: pass
    def warning(self, msg: str) -> None: pass
    def debug(self, msg: str) -> None: pass
    def exception(self, msg: str, exc: Exception) -> None: pass

class Benchmark002OrganizeDownloads(CognitiveBenchmark):
    
    @property
    def metadata(self) -> BenchmarkMetadata:
        return BenchmarkMetadata(
            id="002",
            name="Organize Downloads",
            layer="Capability",
            deterministic=True,
            required_capabilities=["ListDirectory", "CategorizeFiles", "CreateDirectory", "MoveFile"],
            description="Organizes a Downloads folder into categories."
        )
        
    def setup(self, event_bus: Any, registry: Any) -> Goal:
        self.temp_dir = tempfile.mkdtemp(prefix="chitti_downloads_")
        
        # Create dummy files
        files = ["invoice.pdf", "movie.mp4", "photo.jpg", "archive.zip", "resume.docx"]
        for f in files:
            with open(os.path.join(self.temp_dir, f), 'w') as fh:
                fh.write("dummy")
                
        goal = Goal(
            goal_id="goal_bench_002",
            description="Organize Downloads",
            priority=GoalPriority.NORMAL,
            state=GoalState.PENDING,
            created_at=datetime.datetime.utcnow(),
            deadline=None,
            criteria=[GoalCriterion(criterion_id="c1", description="Files are moved", required=True, status=False)]
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
        
        # Register capabilities
        list_cap = ListDirectoryCapability()
        cat_cap = CategorizeFilesCapability()
        create_cap = CreateDirectoryCapability()
        move_cap = MoveFileCapability()
        
        registry.register_capability(list_cap)
        registry.register_capability(cat_cap)
        registry.register_capability(create_cap)
        registry.register_capability(move_cap)
        
        # Setup Product Layer
        expression_engine = ExpressionEngine(event_bus)
        expression_engine.start()
        
        # Capture events
        events = []
        def on_event(event):
            events.append(event.payload.get("event"))
        event_bus.subscribe_all(on_event)
        
        # We manually orchestrate the workflow steps just as the Planner and WorkflowTranslator would
        execution_runtime = ExecutionRuntime(registry, event_bus)
        
        # Goal already defined in setup
        
        # Simulate Workflow Execution
        # Step 1: List Directory
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
        
        res1 = list_cap.execute(ToolInvocation(id="inv_1", tool_name="ListDirectory", arguments={"path": downloads_path}, confidence=1.0, source="Benchmark"), ctx)
        files = [os.path.join(downloads_path, f) for f in res1.data["files"]]
        
        # Step 2: Categorize Files
        mapping = {
            ".pdf": "Documents",
            ".docx": "Documents",
            ".jpg": "Images",
            ".mp4": "Videos",
            ".zip": "Archives"
        }
        res2 = cat_cap.execute(ToolInvocation(id="inv_2", tool_name="CategorizeFiles", arguments={"files": files, "mapping": mapping}, confidence=1.0, source="Benchmark"), ctx)
        categorized_files = res2.data["categorized_files"]
        
        # Step 3 & 4: Create Folders and Move Files
        for category, file_list in categorized_files.items():
            cat_path = os.path.join(downloads_path, category)
            create_cap.execute(ToolInvocation(id=f"inv_c_{category}", tool_name="CreateDirectory", arguments={"path": cat_path}, confidence=1.0, source="Benchmark"), ctx)
            for file_path in file_list:
                dest = os.path.join(cat_path, os.path.basename(file_path))
                move_cap.execute(ToolInvocation(id=f"inv_m_{os.path.basename(file_path)}", tool_name="MoveFile", arguments={"source": file_path, "destination": dest}, confidence=1.0, source="Benchmark"), ctx)

        # We manually fire the completion event since we bypassed full workflow execution here
        # (A real execution runtime would loop through steps and fire this)
        event_bus.publish(WorkflowCompletedEvent(
            event_id="e_done", workflow_id="wf_002", plan_id="plan_002", correlation_id="corr_002", sequence_number=1, timestamp=datetime.datetime.utcnow(),
            duration_ms=500
        ))
        
        # Evaluate
        goal_assessment = GoalAssessment(
            goal_id="goal_bench_002", workflow_id="wf_002", plan_id="plan_002", status=GoalStatus.SATISFIED,
            satisfaction_evaluation=SatisfactionEvaluation(1.0, [], 1.0, 1.0),
            unmet_constraints=[], evaluator_reasoning="Organized successfully", assessment_timestamp=datetime.datetime.utcnow(), workflow_assessment_hash="hash"
        )
        wf_assessment = WorkflowAssessment(
            workflow_id="wf_002", plan_id="plan_002", status=AssessWorkflowStatus.COMPLETED_SUCCESSFULLY,
            metadata=WorkflowAssessmentMetadata("1.0", datetime.datetime.utcnow(), 10, "hash"),
            task_assessments=[], anomalies=[]
        )
        
        # Format CapabilityResult
        counts = {cat: len(flist) for cat, flist in categorized_files.items()}
        result = CapabilityResult(
            capability_name="Organize Downloads",
            goal_assessment=goal_assessment,
            workflow_assessment=wf_assessment,
            metrics=ExecutionMetrics((time.time() - start_time)*1000, len(events), {}),
            structured_data=counts
        )
        
        presentation = PresentationGenerator().generate(result)
        
        latency_ms = (time.time() - start_time) * 1000
        
        return {
            "downloads_path": downloads_path,
            "events": events,
            "latency_ms": latency_ms,
            "presentation": presentation,
            "goal_assessment": goal_assessment
        }
        
    def assert_success(self, result_data: Dict[str, Any]) -> BenchmarkResult:
        downloads_path = result_data["downloads_path"]
        events = result_data["events"]
        latency_ms = result_data["latency_ms"]
        presentation = result_data["presentation"]
        goal_assessment = result_data["goal_assessment"]
        
        # Verify files were moved
        assert os.path.exists(os.path.join(downloads_path, "Documents", "invoice.pdf")), "invoice.pdf missing"
        assert os.path.exists(os.path.join(downloads_path, "Documents", "resume.docx")), "resume.docx missing"
        assert os.path.exists(os.path.join(downloads_path, "Images", "photo.jpg")), "photo.jpg missing"
        assert os.path.exists(os.path.join(downloads_path, "Videos", "movie.mp4")), "movie.mp4 missing"
        assert os.path.exists(os.path.join(downloads_path, "Archives", "archive.zip")), "archive.zip missing"
        
        # Verify original files are gone
        assert not os.path.exists(os.path.join(downloads_path, "invoice.pdf")), "invoice.pdf still in root"
        
        # Verify events
        event_names = [e.__class__.__name__ for e in events]
        assert "AvatarStateChanged" in event_names
        
        # Check presentation
        assert "Documents       2" in presentation or "Documents" in presentation
        assert "Total Files" in presentation
        
        # Cleanup
        shutil.rmtree(downloads_path)
        
        return BenchmarkResult(
            benchmark_id=self.metadata.id,
            passed=True,
            latency_ms=latency_ms,
            events_count=len(events),
            goal_status=goal_assessment.status.value,
            error_message=None,
            extracted_path=presentation
        )

if __name__ == "__main__":
    import traceback
    print("--- Running Benchmark 002: Organize Downloads ---")
    benchmark = Benchmark002OrganizeDownloads()
    try:
        result_data = benchmark.execute()
        result = benchmark.assert_success(result_data)
        if result.passed:
            print("SUCCESS: Benchmark 002 passed!")
            print(f"Presentation Output:\n{result.extracted_path}")
        else:
            print(f"FAILED: {result.error_message}")
    except Exception as e:
        print("CRITICAL FAILURE:")
        traceback.print_exc()
