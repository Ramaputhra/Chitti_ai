import asyncio
from datetime import datetime
from desktop.models.events import KernelShutdownRequest
from desktop.models.presentation import RenderedExpression
from desktop.app.transports import ITransport

class DeveloperShell(ITransport):
    """
    Product Validation testing shell that acts as an isolated transport.
    """
    def __init__(self, runner_callback=None):
        self._running = False
        self._task = None
        self.runner_callback = runner_callback
        self.on_input = None
        
    async def start(self):
        self._running = True
        print("\n===================================")
        print("CHITTI V1.1 Product Validation Runner")
        print("Type '/restart' to reboot kernel, '/exit' to stop.")
        print("===================================\n")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
        print("\n[DeveloperShell] Stopped.")

    async def run(self):
        """Blocking REPL that owns the test session lifetime."""
        loop = asyncio.get_event_loop()
        while self._running:
            try:
                line = await loop.run_in_executor(None, input, "CHITTI > ")
                text = line.strip()
                if not text:
                    continue
                    
                if text.lower() in ["/exit", "/quit", "exit", "quit"]:
                    if self.runner_callback:
                        self.runner_callback("exit")
                    break
                    
                if text.lower() == "/restart":
                    if self.runner_callback:
                        self.runner_callback("restart")
                    break
                    
                if self.on_input:
                    if asyncio.iscoroutinefunction(self.on_input):
                        await self.on_input(text, "DeveloperShell")
                    else:
                        self.on_input(text, "DeveloperShell")
                    
            except (EOFError, KeyboardInterrupt):
                if self.runner_callback:
                    self.runner_callback("exit")
                break
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[DeveloperShell] Input Error: {e}")

    async def deliver(self, expr: RenderedExpression, event_bus):
        if "text" in expr.formats:
            print(f"\nCHITTI: {expr.formats['text']}\n")
