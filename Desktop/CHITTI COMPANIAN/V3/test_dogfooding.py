import sys
import os
import asyncio

v3_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, v3_root)

from desktop.app.kernel import BootManager, RuntimeConfiguration
from desktop.app.capability_contracts import SimpleCapabilityRegistry, CapabilityDescriptor
from desktop.models.events import Event
from desktop.models.interaction import InteractionEnvelope
import uuid

async def run_test():
    config = RuntimeConfiguration(use_llm=True, transport="developer")
    boot = BootManager(config=config)
    boot.is_demo_mode = False
    
    cap_registry = SimpleCapabilityRegistry()
    
    from desktop.packages.productivity_workspace_pack.capabilities.resume_activity import ResumeActivityCapability
    from desktop.packages.desktop_pack.capabilities.execution import LaunchApplicationCapability, ExecuteTerminalCommandCapability
    from desktop.packages.desktop_pack.capabilities.expression import TextResponseCapability, ExpressionCapability, SpeakCapability
    from desktop.packages.file_pack.capabilities.search import FindFileCapability
    from desktop.packages.browser_pack.capabilities.navigation import OpenBrowserCapability
    from desktop.capabilities.search.distance import DistanceCapability
    
    cap_registry.register(CapabilityDescriptor(id="ResumeActivityCapability", version="1.0", permissions=["workspace"], execution_mode="sync", factory=lambda: ResumeActivityCapability()))
    cap_registry.register(CapabilityDescriptor(id="LaunchApplicationCapability", version="1.0", permissions=["execution"], execution_mode="sync", factory=lambda: LaunchApplicationCapability()))
    cap_registry.register(CapabilityDescriptor(id="ExecuteTerminalCommandCapability", version="1.0", permissions=["execution"], execution_mode="sync", factory=lambda: ExecuteTerminalCommandCapability()))
    cap_registry.register(CapabilityDescriptor(id="TextResponseCapability", version="1.0", permissions=["expression"], execution_mode="sync", factory=lambda: TextResponseCapability()))
    cap_registry.register(CapabilityDescriptor(id="ExpressionCapability", version="1.0", permissions=["expression"], execution_mode="sync", factory=lambda: ExpressionCapability()))
    cap_registry.register(CapabilityDescriptor(id="SpeakCapability", version="1.0", permissions=["expression"], execution_mode="sync", factory=lambda: SpeakCapability()))
    cap_registry.register(CapabilityDescriptor(id="FindFileCapability", version="1.0", permissions=["filesystem"], execution_mode="sync", factory=lambda: FindFileCapability()))
    cap_registry.register(CapabilityDescriptor(id="OpenBrowserCapability", version="1.0", permissions=["web"], execution_mode="sync", factory=lambda: OpenBrowserCapability()))
    cap_registry.register(CapabilityDescriptor(id="DistanceCapability", version="1.0", permissions=["location"], execution_mode="sync", factory=lambda: DistanceCapability()))
    
    from desktop.app.presentation_contracts import DefaultTextRenderer, MarkdownRenderer
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    
    boot.compose_runtimes(cap_registry=cap_registry, renderers=renderers)
    
    await boot.initialize()
    kernel = await boot.start()
    
    kernel_task = asyncio.create_task(kernel.run())
    
    async def send_msg(text):
        print(f"\n--- USER: {text} ---")
        msg = InteractionEnvelope(
            id=str(uuid.uuid4()),
            correlation_id=str(uuid.uuid4()),
            source="developer",
            payload=text
        )
        await kernel.context.event_bus.publish(msg)
        await asyncio.sleep(6.0) # Wait for LLM and capabilities to run
        
    # Wait for boot
    await asyncio.sleep(2.0)
    
    await send_msg("what is my first message to you?")
    await send_msg("what is capital of Telangana?")
    await send_msg("open youtube and play any song")
    await send_msg("find distance to Ameerpet from yousufguda")
    await send_msg("remember this plan of execution in your memory")
    await send_msg("close calculator")
    
    print("\nShutting down...")
    await kernel.shutdown()
    kernel_task.cancel()

if __name__ == "__main__":
    asyncio.run(run_test())
