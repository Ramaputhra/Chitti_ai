import asyncio
from desktop.runtimes.workflow.models import (
    Goal, ActionStep, SequentialStep, WaitStep, WorkflowContext
)
from desktop.runtimes.workflow.workflow_runtime import WorkflowRuntime
from desktop.capabilities.screen_understanding.capability import ScreenUnderstandingCapability

class MockLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")
    def warning(self, msg): print(f"WARN: {msg}")

class MockAIRuntime:
    pass

async def execute_demo():
    logger = MockLogger()
    wf_runtime = WorkflowRuntime(logger, None)
    wf_runtime.initialize()
    
    # We stub the capability execution here since we don't have the full CapabilityRuntime wired in the test.
    screen_cap = ScreenUnderstandingCapability(MockAIRuntime())
    
    # Goal: Summarize the current screen context
    goal = Goal(
        id="goal_analyze",
        description="Summarize what the user is currently doing.",
        priority=1
    )
    
    logger.info("Planner formulated workflow to analyze screen.")
    
    workflow_definition = SequentialStep([
        WaitStep(timeout_ms=100), # Simulating waiting for app to open
        ActionStep(capability="Screen.Understand", intent_payload={}),
        ActionStep(capability="Notification.Send", intent_payload={"summary_var": "screen_summary"})
    ])
    
    # We'll run the capability manually to inject the result into context for the demo
    result = await screen_cap.execute({})
    
    # Planner generates summary based on the result
    summary = f"You're editing '{result.screen_model.document}' in {result.screen_model.application}. Intent: {result.screen_model.current_intent.name}."
    
    context = WorkflowContext()
    context.variables["screen_summary"] = summary
    
    wf_id = await wf_runtime.submit_workflow(workflow_definition, context)
    await wf_runtime.execute_workflow(wf_id)
    
    print(f"\nFinal Summary Notification Payload:\n{summary}")
    
    wf_runtime.shutdown()

if __name__ == "__main__":
    asyncio.run(execute_demo())
