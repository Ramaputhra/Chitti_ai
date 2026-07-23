import asyncio
from desktop.app.kernel import BootManager
from desktop.models.interaction import ExpressionRequested, ExpressionType
from desktop.models.presentation import RenderedExpression, AvatarStateChanged, ExpressionDelivered
from desktop.runtimes.expression import ExpressionRuntime
from desktop.app.presentation_contracts import DefaultTextRenderer, MarkdownRenderer
from desktop.runtimes.memory import MemoryRuntime
from desktop.platform.inference.memory.dict_provider import DictMemoryProvider
from desktop.app.memory_contracts import IMemoryService

async def verify_expression_runtime():
    print("--- Expression Runtime Verification (Sprint 81) ---")
    
    boot = BootManager()
    
    # 1. Setup Runtimes
    provider = DictMemoryProvider()
    mem_runtime = MemoryRuntime(provider)
    
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    expr_runtime = ExpressionRuntime(renderers)
    
    boot.runtimes.extend([mem_runtime, expr_runtime])
    
    success = await boot.initialize()
    assert success
    kernel = await boot.start()
    event_bus = kernel.context.event_bus

    # Trackers for Demo
    captured_rendered = []
    captured_avatars = []
    
    async def on_rendered(expr: RenderedExpression):
        captured_rendered.append(expr)
        
    async def on_avatar(state: AvatarStateChanged):
        captured_avatars.append(state)
        print(f"[Demo UI] Avatar State changed to: {state.state.name}")

    event_bus.subscribe(RenderedExpression, on_rendered)
    event_bus.subscribe(AvatarStateChanged, on_avatar)

    # --- Scenario 1: Multi-format rendering & Scenario 2: AvatarStateChanged ---
    print("\n[Scenario 1 & 2] Publishing ExpressionRequested")
    
    req = ExpressionRequested(
        interaction_id="inter_123",
        expression_type=ExpressionType.SPEAK,
        payload="Hello from the cognitive pipeline!",
        emotion="FRIENDLY"
    )
    
    event_bus.publish(req)
    await asyncio.sleep(0.1) # Yield to let runtime process
    
    assert len(captured_rendered) == 1
    rendered = captured_rendered[0]
    
    print("\n✅ Scenario 1: Multi-format rendering successful.")
    print(f"   Formats available: {list(rendered.formats.keys())}")
    print(f"   Text format: {rendered.formats['text']}")
    print(f"   Markdown format: {rendered.formats['markdown']}")
    
    print("\n✅ Scenario 2: Avatar state tracking successful.")
    assert len(captured_avatars) == 1
    assert captured_avatars[0].state.name == "SPEAKING"
    
    # --- Scenario 3: Memory Delivery Confirmation ---
    print("\n[Scenario 3] Transport Confirmation & Memory")
    
    delivery = ExpressionDelivered(
        interaction_id="inter_123",
        session_id="session_1",
        delivered_format="text",
        content=rendered.formats["text"]
    )
    
    event_bus.publish(delivery)
    await asyncio.sleep(0.1)
    
    memory: IMemoryService = boot.registry.resolve(IMemoryService)
    history = memory.get_recent_interactions("session_1")
    
    assert len(history) == 1
    assert history[0].role == "assistant"
    assert history[0].content == "[FRIENDLY] Hello from the cognitive pipeline!"
    print("\n✅ Scenario 3: Memory successfully ingested the delivered expression as a fact (Rule 175).")
    
    # Wait for Avatar to revert to IDLE
    await asyncio.sleep(1.0)
    assert len(captured_avatars) == 2
    assert captured_avatars[1].state.name == "IDLE"

    await kernel.shutdown()

if __name__ == "__main__":
    asyncio.run(verify_expression_runtime())
