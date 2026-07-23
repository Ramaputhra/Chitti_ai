import asyncio
from datetime import datetime
from desktop.capabilities.screen_understanding.models import ScreenModel, CurrentIntent
from desktop.capabilities.context_synthesis.capability import ContextSynthesisCapability

class MockWorldRuntime:
    def get_latest_screen_model(self):
        return ScreenModel(
            active_window="models.py - Code",
            application="Code.exe",
            document="models.py",
            selection=None,
            controls=[],
            relationships=[],
            tasks=["Editing Python"],
            current_intent=CurrentIntent.CODING,
            confidence=0.9,
            perception_quality="deterministic",
            timestamp=datetime.now()
        )

class MockAIRuntime:
    pass

async def execute_demo():
    print("--- Desktop Context Demonstration ---\n")
    
    world_runtime = MockWorldRuntime()
    ai_runtime = MockAIRuntime()
    capability = ContextSynthesisCapability(world_runtime, ai_runtime)
    
    # 1. Planner asks "What is the user doing right now?"
    # It doesn't invoke ScreenUnderstanding. It invokes ContextSynthesis.
    context = await capability.execute({})
    
    # 2. Output the synthesized context (which pulled from the World Runtime + Extractors)
    print("Synthesized Context from World State:")
    print(f"Task: {context.current_task.value} (Confidence: {context.current_task.confidence})")
    print(f"Intent: {context.user_work_intent.value.name} (Confidence: {context.user_work_intent.confidence})")
    print(f"Project: {context.current_project.value}")
    print(f"Activity: {context.current_activity.value}")
    
    print("\nWorking Set:")
    for f in context.working_set.value.active_files:
        print(f" - {f}")
        
    print("\nCoding Context:")
    if context.coding_context.value:
        print(f" - Branch: {context.coding_context.value['branch']}")
        print(f" - Modified Files: {context.coding_context.value['modified_files']}")
    
    # 3. Simulate identical screen (cache hit)
    print("\nSimulating unchanged screen...")
    context_cached = await capability.execute({})
    print(f"Cache hit: {context_cached is context}")

if __name__ == "__main__":
    asyncio.run(execute_demo())
