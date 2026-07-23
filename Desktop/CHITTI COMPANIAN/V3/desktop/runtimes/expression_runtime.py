import asyncio
from typing import List
from desktop.models.lifecycle import IRuntime, HealthState
from desktop.models.interaction import ExpressionRequested
from desktop.models.presentation import RenderedExpression, AvatarStateChanged, AvatarState
from desktop.app.context import KernelContext
from desktop.app.presentation_contracts import IExpressionRenderer

class ExpressionRuntime(IRuntime):
    """
    The Presentation Boundary (Rule 179).
    Translates abstract cognitive intent into multi-format presentation artifacts.
    """
    def __init__(self, renderers: List[IExpressionRenderer]):
        self.renderers = renderers
        self.context = None

    @property
    def dependencies(self):
        return []

    async def initialize(self, context: KernelContext) -> bool:
        self.context = context
        # Subscribe to abstract requests originating from executing capabilities (Rule 180)
        context.event_bus.subscribe(ExpressionRequested, self._on_expression_requested)
        return True

    async def start(self) -> bool:
        print(f"    [ExpressionRuntime] Started with {len(self.renderers)} renderers.")
        return True

    async def stop(self) -> bool:
        print("    [ExpressionRuntime] Stopped.")
        return True

    def health(self) -> HealthState:
        return HealthState.HEALTHY

    async def shutdown(self) -> bool:
        return True

    async def _on_expression_requested(self, req: ExpressionRequested):
        """Intercepts an executing capability's intent to express."""
        print(f"\n[Expression] Rendering multi-format output for interaction: {req.interaction_id}")
        
        # 1. State Transition: Emit AvatarState (Separated from Rendering)
        # In a real system, we might map `req.emotion` to specific avatar animations.
        self.context.event_bus.publish(AvatarStateChanged(state=AvatarState.SPEAKING))
        
        # 2. Rendering: Multi-format generation (Rule 181 - Lossless)
        formats = {}
        for renderer in self.renderers:
            fmt = renderer.get_format_name()
            try:
                formats[fmt] = renderer.render(req)
            except Exception as e:
                print(f"[Expression] ⚠️ Renderer {fmt} failed: {e}")
                
        # 3. Artifact Packaging
        rendered_expr = RenderedExpression(
            interaction_id=req.interaction_id,
            correlation_id=req.correlation_id,
            formats=formats,
            metadata={"emotion": req.emotion, "type": req.expression_type.name}
        )
        
        # 4. Handoff to Output Transports
        self.context.event_bus.publish(rendered_expr)
        
        # 5. State Transition: Revert AvatarState
        # (Using a small delay in this demo to simulate speaking time)
        asyncio.create_task(self._revert_avatar_state())
        
    async def _revert_avatar_state(self):
        await asyncio.sleep(1.0)
        if self.context:
            self.context.event_bus.publish(AvatarStateChanged(state=AvatarState.IDLE))
