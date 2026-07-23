import sys
import os
import asyncio

v3_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, v3_root)

from desktop.app.kernel import BootManager, RuntimeConfiguration
from desktop.runtimes.capability.registry import CapabilityRegistry
from desktop.models.interaction import InteractionEnvelope
import uuid
import logging

sys.stdout = open('test_output.txt', 'w', encoding='utf-8')
logging.basicConfig(level=logging.INFO)

async def run_test():
    config = RuntimeConfiguration(use_llm=True, transport="developer")
    boot = BootManager(config=config)
    
    cap_registry = CapabilityRegistry()
    
    from desktop.app.presentation_contracts import DefaultTextRenderer, MarkdownRenderer
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    
    boot.compose_runtimes(cap_registry=cap_registry, renderers=renderers)
    
    await boot.initialize()
    kernel = await boot.start()
    
    kernel_task = asyncio.create_task(kernel.run())
    
    async def send_msg(text):
        print(f"\n======================================")
        print(f"--- USER INPUT: {text} ---")
        print(f"======================================")
        msg = InteractionEnvelope(
            id=str(uuid.uuid4()),
            correlation_id=str(uuid.uuid4()),
            origin="developer",
            transport="developer",
            payload=text
        )
        kernel.context.event_bus.publish(msg)
        await asyncio.sleep(8.0) # wait for LLM
        
    await asyncio.sleep(2.0)
    
    queries = [
        "Execute command get_identity",
        "hello",
        "what is 2+2",
        "open calculator",
        "close calculator",
        "Perform unknown action"
    ]
    
    for q in queries:
        await send_msg(q)
    
    print("\nShutting down...")
    await kernel.shutdown()
    kernel_task.cancel()

if __name__ == "__main__":
    asyncio.run(run_test())
