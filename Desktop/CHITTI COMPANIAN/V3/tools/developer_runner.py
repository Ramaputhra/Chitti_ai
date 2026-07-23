import sys
import os
import asyncio

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, v3_root)

from desktop.app.kernel import BootManager
from desktop.runtimes.memory_runtime import MemoryRuntime
from desktop.runtimes.planner import PlannerRuntime
from desktop.runtimes.execution import ExecutionRuntime
from desktop.runtimes.expression_runtime import ExpressionRuntime
from desktop.runtimes.conversation.runtime import ConversationRuntime
from desktop.runtimes.ai.runtime import AIRuntime
from desktop.runtimes.inference.runtime import InferenceRuntime
from desktop.platform.strategies.deterministic_planner import DeterministicPlannerStrategy
from desktop.platform.inference.inference.gguf_provider import GGUFInferenceProvider
from desktop.app.capability_contracts import SimpleCapabilityRegistry
from desktop.packages.productivity_workspace_pack.capabilities.resume_activity import ResumeActivityCapability
from desktop.app.capability_contracts import CapabilityDescriptor as CoreCapabilityDescriptor
from desktop.app.presentation_contracts import DefaultTextRenderer
from desktop.app.transports import TransportManager

# Import tools
from tools.developer_shell import DeveloperShell
from tools.diagnostics import DiagnosticsObserver
from desktop.models.events import Event

async def run_developer_mode():
    from desktop.app.kernel import RuntimeConfiguration
    config = RuntimeConfiguration(use_llm=True, transport="developer")
    
    while True:
        print("\n--- Booting CHITTI Cognitive Engine (Architecture Validation) ---")
        
        boot = BootManager(config=config)
        boot.is_demo_mode = False
        
        from desktop.app.capability_contracts import SimpleCapabilityRegistry
        cap_registry = SimpleCapabilityRegistry()
        
        from desktop.packages.productivity_workspace_pack.capabilities.resume_activity import ResumeActivityCapability
        from desktop.packages.desktop_pack.capabilities.execution import LaunchApplicationCapability, ExecuteTerminalCommandCapability
        from desktop.packages.desktop_pack.capabilities.expression import TextResponseCapability, ExpressionCapability, SpeakCapability
        from desktop.packages.file_pack.capabilities.search import FindFileCapability
        from desktop.packages.browser_pack.capabilities.navigation import OpenBrowserCapability
        from desktop.capabilities.search.distance import DistanceCapability
        from desktop.app.capability_contracts import CapabilityDescriptor as CoreCapabilityDescriptor
        try:
            cap = ResumeActivityCapability()
            cap_descriptor = CoreCapabilityDescriptor(
                id="ResumeActivityCapability", 
                version="1.0", 
                permissions=["workspace", "execution"], 
                execution_mode="sync", 
                factory=lambda: cap
            )
            cap_registry.register(cap_descriptor)
            
            launch_cap = LaunchApplicationCapability()
            launch_descriptor = CoreCapabilityDescriptor(
                id="LaunchApplicationCapability", 
                version="1.0", 
                permissions=["execution"], 
                execution_mode="sync", 
                factory=lambda: launch_cap
            )
            cap_registry.register(launch_descriptor)
            
            term_cap = ExecuteTerminalCommandCapability()
            term_descriptor = CoreCapabilityDescriptor(
                id="ExecuteTerminalCommandCapability",
                version="1.0",
                permissions=["execution"],
                execution_mode="sync",
                factory=lambda: term_cap
            )
            cap_registry.register(term_descriptor)
            
            text_cap = TextResponseCapability()
            text_cap.event_bus = boot.context.event_bus
            text_descriptor = CoreCapabilityDescriptor(
                id="TextResponseCapability", 
                version="1.0", 
                permissions=["expression"], 
                execution_mode="sync", 
                factory=lambda: text_cap
            )
            cap_registry.register(text_descriptor)
            
            expr_cap = ExpressionCapability()
            expr_cap.event_bus = boot.context.event_bus
            expr_descriptor = CoreCapabilityDescriptor(
                id="ExpressionCapability", 
                version="1.0", 
                permissions=["expression"], 
                execution_mode="sync", 
                factory=lambda: expr_cap
            )
            cap_registry.register(expr_descriptor)
            
            speak_cap = SpeakCapability()
            speak_cap.event_bus = boot.context.event_bus
            speak_descriptor = CoreCapabilityDescriptor(
                id="SpeakCapability", 
                version="1.0", 
                permissions=["expression"], 
                execution_mode="sync", 
                factory=lambda: speak_cap
            )
            cap_registry.register(speak_descriptor)
            
            find_cap = FindFileCapability()
            find_descriptor = CoreCapabilityDescriptor(
                id="FindFileCapability",
                version="1.0",
                permissions=["filesystem"],
                execution_mode="sync",
                factory=lambda: find_cap
            )
            cap_registry.register(find_descriptor)
            
            browser_cap = OpenBrowserCapability()
            browser_descriptor = CoreCapabilityDescriptor(
                id="OpenBrowserCapability",
                version="1.0",
                permissions=["web"],
                execution_mode="sync",
                factory=lambda: browser_cap
            )
            cap_registry.register(browser_descriptor)
            
            distance_cap = DistanceCapability()
            distance_descriptor = CoreCapabilityDescriptor(
                id="DistanceCapability",
                version="1.0",
                permissions=["web", "location"],
                execution_mode="sync",
                factory=lambda: distance_cap
            )
            cap_registry.register(distance_descriptor)
        except Exception as e:
            print(f"Capability Registration Error: {e}")
            
        from desktop.app.presentation_contracts import DefaultTextRenderer, MarkdownRenderer
        renderers = [DefaultTextRenderer(), MarkdownRenderer()]
        
        # EXACT PRODUCTION BOOT SEQUENCE
        boot.compose_runtimes(cap_registry=cap_registry, renderers=renderers)
        
        success = await boot.initialize()
        if not success:
            print("❌ Boot initialization failed.")
            sys.exit(1)
            
        kernel = await boot.start()
        
        # Attach DiagnosticsObserver AFTER boot
        diag_observer = DiagnosticsObserver()
        diag_observer.attach(kernel)
        
        # Setup Shell
        transport_mgr = TransportManager(kernel)
        shell = DeveloperShell()
        transport_mgr.register(shell)
        
        # Hook up RenderedExpression for DeveloperShell
        from desktop.models.presentation import RenderedExpression
        kernel.context.event_bus.subscribe(RenderedExpression, transport_mgr._on_rendered_expression)
        
        await transport_mgr.start_all()
        
        action = None
        def runner_callback(cmd_action):
            nonlocal action
            action = cmd_action

        shell.runner_callback = runner_callback
        
        # Run Kernel loop in background
        kernel_task = asyncio.create_task(kernel.run())
        
        # Shell owns lifetime, blocks here until user exits
        await shell.run()
        
        print("\nShutting down...")
        kernel_task.cancel()
        await transport_mgr.stop_all()
        await kernel.shutdown()
        
        if action == "restart":
            print("\n[DeveloperRunner] Restarting...\n")
            continue
        else:
            break

if __name__ == "__main__":
    try:
        asyncio.run(run_developer_mode())
    except KeyboardInterrupt:
        print("\nExit.")
