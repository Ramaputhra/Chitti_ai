import sys
import os
import threading
import asyncio

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, v3_root)

from desktop.app.kernel import BootManager
from desktop.runtimes.memory_runtime import MemoryRuntime
from desktop.runtimes.planner import PlannerRuntime
from desktop.runtimes.execution import ExecutionRuntime
from desktop.runtimes.expression_runtime import ExpressionRuntime
from desktop.platform.strategies.deterministic_planner import DeterministicPlannerStrategy
from desktop.app.transports import TransportManager, CLITransport
from desktop.ui.tray import SystemTray
from desktop.ui.widget.companion_widget import CompanionWidget
from desktop.ui.presence.controller import PresenceController
from desktop.ui.presence.engine import PresenceEngine
from desktop.app.diagnostics import PipelineValidator
from desktop.models.events import Event
from PySide6.QtWidgets import QApplication

async def boot_kernel(boot, cap_registry, transport_mgr, time_runtime, engine):
    # Manual capability registration has been removed in favor of dynamic package discovery.
    pass

    success = await boot.initialize()
    if not success:
        print("❌ Boot initialization failed.")
        sys.exit(1)
        
    kernel = await boot.start()
    
    validator = PipelineValidator(kernel)
    
    # Setup Transports
    transport_mgr.kernel = kernel
    from desktop.models.interaction import RenderedExpression
    kernel.context.event_bus.subscribe(RenderedExpression, transport_mgr._on_rendered_expression)
    
    transport_mgr.register(CLITransport())
    
    from desktop.app.voice_transport import VoiceTransport
    transport_mgr.register(VoiceTransport())
    
    await transport_mgr.start_all()
    engine.start()
    
    print("\n✅ System Ready. Background Thread Running.\n")
    
    kernel_task = asyncio.create_task(kernel.run() if hasattr(kernel, 'run') else _mock_wait(kernel))
    try:
        await kernel_task
    except asyncio.CancelledError:
        pass
    
    print("\nShutting down transports...")
    await transport_mgr.stop_all()
    engine.stop()
    print("CHITTI Shutdown Complete.")

async def _mock_wait(kernel):
    while getattr(kernel, "_running", True):
        await asyncio.sleep(0.1)

def run_kernel_thread(boot, cap_registry, transport_mgr, time_runtime, engine):
    asyncio.run(boot_kernel(boot, cap_registry, transport_mgr, time_runtime, engine))

def main():
    import argparse
    parser = argparse.ArgumentParser(description="CHITTI Cognitive Engine")
    parser.add_argument("--demo", action="store_true", help="Launch in stable demo mode")
    parser.add_argument("--use-llm", action="store_true", help="Use real LLM (GGUF Qwen2.5) instead of Deterministic planner")
    args, unknown = parser.parse_known_args()
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    from desktop.app.kernel import RuntimeConfiguration
    config = RuntimeConfiguration(use_llm=args.use_llm)
    boot = BootManager(config=config)
    boot.is_demo_mode = args.demo
    
    from desktop.app.capability_contracts import SimpleCapabilityRegistry
    cap_registry = SimpleCapabilityRegistry()
    
    from desktop.app.presentation_contracts import DefaultTextRenderer, MarkdownRenderer
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    
    boot.compose_runtimes(cap_registry, renderers)
    
    from desktop.runtimes.time_runtime import TimeRuntime
    time_runtime = TimeRuntime()
    
    
    from desktop.productivity.providers.registry import ContextProviderRegistry
    from desktop.productivity.browser.manager import BrowserManager
    from desktop.productivity.providers.clipboard import ClipboardProvider
    from desktop.productivity.providers.explorer import ExplorerProvider
    from desktop.productivity.providers.terminal import TerminalProvider
    from desktop.productivity.providers.editor import EditorProvider
    ContextProviderRegistry.register(BrowserManager())
    ContextProviderRegistry.register(ClipboardProvider())
    ContextProviderRegistry.register(ExplorerProvider())
    ContextProviderRegistry.register(TerminalProvider())
    ContextProviderRegistry.register(EditorProvider())
    
    transport_mgr = TransportManager(None) 
    
    tray = SystemTray(app)
    widget = CompanionWidget()
    controller = PresenceController()
    
    from PySide6.QtGui import QShortcut, QKeySequence
    from desktop.ui.widget.diagnostics_widget import DiagnosticsWidget
    
    diag_widget = DiagnosticsWidget()
    shortcut = QShortcut(QKeySequence("Ctrl+Shift+D"), widget)
    shortcut.activated.connect(diag_widget.show)
    
    controller.state_changed_signal.connect(widget.handle_state_change)
    boot.event_bus.subscribe("UI.RenderTemplate", lambda e: widget.template_requested_signal.emit(e.payload.get("template_name", ""), e.payload.get("template_data", {})))
    
    engine = PresenceEngine(boot.event_bus)
    
    kernel_thread = threading.Thread(
        target=run_kernel_thread, 
        args=(boot, cap_registry, transport_mgr, time_runtime, engine),
        daemon=True
    )
    kernel_thread.start()
    
    print("Starting Qt Event Loop...")
    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutdown via KeyboardInterrupt.")
