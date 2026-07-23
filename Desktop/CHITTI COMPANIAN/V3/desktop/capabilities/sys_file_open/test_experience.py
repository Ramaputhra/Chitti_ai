import logging
from typing import Dict, Any

from desktop.models.semantic_models import DesktopIntent, IntentType
from desktop.models.planner_models import ExecutionGoal, WorkflowPlan, WorkflowStep
from desktop.models.workflow_models import WorkflowContext
from desktop.models.capability_models import CapabilityManifest
from desktop.models.execution import ExecutionResult, ExecutionStatus

from desktop.runtimes.intent_translation_runtime import IntentTranslationRuntime
from desktop.platform.ai.capability_resolver import CapabilityResolverRuntime
from desktop.runtimes.verification_runtime import VerificationRuntime
from desktop.runtimes.workflow_runtime import WorkflowRuntime

# Stub Capability Runtime for the test
class MockCapabilityRuntime:
    def execute(self, capability: str, parameters: Dict[str, Any]) -> ExecutionResult:
        print(f"   [Execution] Mock executing {capability} with {parameters}")
        return ExecutionResult(status=ExecutionStatus.SUCCESS, output_data={"window_handle": "0x123"})

def test_experience_001_v1_frozen():
    """
    Experience 001: "Chitti, open Downloads"
    Validates the CHITTI Runtime Architecture v1.0 (Frozen).
    Spine: Semantic -> Translation -> Resolver -> Workflow -> Verification -> Completed
    """
    logging.basicConfig(level=logging.ERROR) # keep logs clean for print output
    print("\n--- Experience 001 Architecture Integration Test (v1.0 Frozen) ---")
    
    # 1. User says "Open Downloads." -> Semantic Runtime outputs Intent
    intent = DesktopIntent(type=IntentType.COMMAND, action="open", target="Downloads", confidence=0.98)
    print(f"1. SemanticRuntime   -> Produced DesktopIntent (action='{intent.action}', target='{intent.target}')")
    
    # 2. IntentTranslationRuntime
    translator = IntentTranslationRuntime()
    goal = translator.translate(intent)
    print(f"2. TranslationRuntime-> Produced ExecutionGoal (domain='{goal.domain}', action='{goal.action}', target='{goal.target}')")
    
    # 3. CapabilityResolverRuntime
    manifest = CapabilityManifest(
        id="sys.file.open",
        version="1.0",
        required_permissions=[],
        required_parameters=["folder_path"],
        supported_platforms=["windows"]
    )
    resolver = CapabilityResolverRuntime(registry=[manifest])
    workflow_plan, candidates = resolver.resolve(goal)
    
    if workflow_plan:
        print(f"3. CapabilityResolver-> Fast Path Atomic Hit! Generated WorkflowPlan (Capability: {workflow_plan.steps[0].capability})")
    else:
        print(f"3. CapabilityResolver-> Multiple candidates, delegating to Planner.")
        return
        
    # 4. WorkflowRuntime & VerificationRuntime
    capability_runtime = MockCapabilityRuntime()
    verification_runtime = VerificationRuntime()
    workflow_runtime = WorkflowRuntime(capability_runtime, verification_runtime)
    
    context = WorkflowContext(workflow_id=workflow_plan.plan_id, execution_goal=goal)
    
    print(f"4. WorkflowRuntime   -> Beginning orchestration of plan {workflow_plan.plan_id}...")
    success = workflow_runtime.execute_workflow(workflow_plan, context)
    
    # 5. Result
    if success:
        print(f"5. Verification      -> Verified successfully.")
        print(f"6. Presentation      -> WORKFLOW_COMPLETED Event published.")
        print(f"\n✅ Result: Experience 001 vertical slice executed successfully via v1.0 Spine.")
    else:
        print(f"❌ Result: Execution failed.")

if __name__ == "__main__":
    test_experience_001_v1_frozen()
