import asyncio
from typing import List, Callable, Awaitable
from datetime import datetime
from desktop.app.kernel import RuntimeKernel
from desktop.models.interaction import InteractionEnvelope
from desktop.models.presentation import RenderedExpression, ExpressionDelivered
from uuid import uuid4

class ITransport:
    """Base interface for all transports."""
    async def start(self): pass
    async def stop(self): pass

class TransportManager:
    """
    Manages interaction transports outside the Runtime Kernel boundary.
    (Rule 182: Transports are deterministic adapters, not cognitive runtimes).
    """
    def __init__(self, kernel: RuntimeKernel):
        self.kernel = kernel
        self.transports: List[ITransport] = []
        self._running = False
        
        # Subscribe to outgoing expressions
        if self.kernel and hasattr(self.kernel, "context"):
            self.kernel.context.event_bus.subscribe(RenderedExpression, self._on_rendered_expression)

    def register(self, transport: ITransport):
        self.transports.append(transport)
        
    async def start_all(self):
        self._running = True
        for t in self.transports:
            # Wire transport input to kernel
            if hasattr(t, "on_input"):
                t.on_input = self._handle_input
            if hasattr(t, "set_event_bus"):
                t.set_event_bus(self.kernel.context.event_bus)
            await t.start()

    async def stop_all(self):
        self._running = False
        for t in self.transports:
            await t.stop()

    async def _handle_input(self, text: str, source: str):
        """Standardize raw input into an InteractionEnvelope."""
        envelope = InteractionEnvelope(
            id=str(uuid4()),
            correlation_id=str(uuid4()),
            payload=text,
            origin=source,
            transport=source
        )
        self.kernel.context.event_bus.publish(envelope)

    async def _on_rendered_expression(self, expr: RenderedExpression):
        """Route outgoing expression to transports."""
        for t in self.transports:
            if hasattr(t, "deliver"):
                await t.deliver(expr, self.kernel.context.event_bus)


class CLITransport(ITransport):
    """A simple CLI transport."""
    def __init__(self):
        self.on_input: Callable[[str, str], Awaitable[None]] = None
        self._task = None
        self._running = False
        self.event_bus = None
        
    def set_event_bus(self, event_bus):
        self.event_bus = event_bus

    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._read_loop())
        print("    [CLITransport] Started.")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
        print("    [CLITransport] Stopped.")

    async def _read_loop(self):
        # We use a blocking input() in a thread executor to not block the async loop
        loop = asyncio.get_event_loop()
        while self._running:
            try:
                # This is a bit simplified for the demo
                line = await loop.run_in_executor(None, input, "You> ")
                if line.strip() and self.on_input:
                    if line.strip().lower() in ["exit", "quit"]:
                        from desktop.models.events import KernelShutdownRequest
                        from datetime import datetime
                        # Directly broadcast shutdown request to stop kernel
                        if self.event_bus:
                            self.event_bus.publish(KernelShutdownRequest(timestamp=datetime.now(), source="CLITransport"))
                        break
                    await self.on_input(line.strip(), "CLI")
            except (EOFError, KeyboardInterrupt):
                break
            except asyncio.CancelledError:
                break

    async def deliver(self, expr: RenderedExpression, event_bus):
        if "text" in expr.formats:
            print(f"\nCHITTI> {expr.formats['text']}\n")
            # Confirm delivery
            event_bus.publish(ExpressionDelivered(
                timestamp=datetime.now(),
                source="CLITransport",
                correlation_id=expr.correlation_id,
                domain="Presentation",
                action="ExpressionDelivered",
                interaction_id=expr.interaction_id,
                session_id="default_session", # Simplified for now
                delivered_format="text",
                content=expr.formats['text']
            ))
