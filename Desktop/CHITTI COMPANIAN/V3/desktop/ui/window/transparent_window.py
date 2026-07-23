import logging
from typing import Dict, Any, Optional
from desktop.ui.runtime.runtime_state_machine import RuntimeStateMachine, WindowLifecycleState
from desktop.ui.window.window_layers import SemanticWindowLayer
from desktop.ui.window.window_attachment import WindowAttachment

logger = logging.getLogger(__name__)

class TransparentWindow:
    """
    S36D-1-R1: Generic Base Desktop Window with Semantic Window Layering & Generic Window Attachment API.
    Frameless, Transparent, Always On Top, Rounded Corners, Soft Shadow, Per-Pixel Alpha.
    Generic instance: DOES NOT know business widget content.
    """
    def __init__(self, window_id: str, window_type: str = "GenericWindow", layer: SemanticWindowLayer = SemanticWindowLayer.FLOATING_WIDGET, x: int = 100, y: int = 100, width: int = 360, height: int = 240):
        self.window_id = window_id
        self.window_type = window_type
        self.layer = layer
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.opacity = 1.0
        self.scale = 1.0
        self.click_through = False
        self.always_on_top = True
        self.docked = False
        self.dock_edge: Optional[str] = None
        self.attachment = WindowAttachment(self.window_id)
        self.state_machine = RuntimeStateMachine(initial_state=WindowLifecycleState.CREATED)

    def show(self):
        self.state_machine.transition_to(WindowLifecycleState.VISIBLE)
        logger.info(f"[TransparentWindow] Window '{self.window_id}' ({self.window_type}, Layer: {self.layer.name}) SHOWN at ({self.x}, {self.y}).")

    def hide(self):
        self.state_machine.transition_to(WindowLifecycleState.HIDDEN)
        logger.info(f"[TransparentWindow] Window '{self.window_id}' HIDDEN.")

    def move(self, new_x: int, new_y: int):
        self.x = new_x
        self.y = new_y
        logger.info(f"[TransparentWindow] Window '{self.window_id}' MOVED to ({self.x}, {self.y}).")

    def resize(self, w: int, h: int):
        self.width = w
        self.height = h

    def set_click_through(self, enabled: bool):
        self.click_through = enabled

    def dock(self, edge: str = "right"):
        self.docked = True
        self.dock_edge = edge
        self.state_machine.transition_to(WindowLifecycleState.DOCKED)

    def undock(self):
        self.docked = False
        self.dock_edge = None
        self.state_machine.transition_to(WindowLifecycleState.FLOATING)

    def destroy(self):
        self.attachment.detach()
        self.state_machine.transition_to(WindowLifecycleState.DESTROYED)
        logger.info(f"[TransparentWindow] Window '{self.window_id}' DESTROYED.")
