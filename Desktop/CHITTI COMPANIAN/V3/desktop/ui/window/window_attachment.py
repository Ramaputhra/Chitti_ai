import logging
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

class WindowAttachment:
    """
    S36D-1-R1: Generic Window Attachment API supporting:
    - Character Anchor (consumes Character Anchor API ONLY)
    - Desktop Coordinate
    - Screen Edge
    - Mouse Position
    - Runtime Session
    Contracts: attach(), detach(), move(), follow(), release(), update_anchor().
    """
    def __init__(self, window_id: str):
        self.window_id = window_id
        self.target_type: str = "NONE"  # "CHARACTER_ANCHOR", "DESKTOP_COORD", "SCREEN_EDGE", "MOUSE_POS", "RUNTIME_SESSION"
        self.anchor_data: Dict[str, Any] = {}
        self.offset_x: int = 10
        self.offset_y: int = 0
        self.is_attached: bool = False
        self.is_following: bool = False

    def attach(self, target_type: str, anchor_data: Dict[str, Any], offset_x: int = 10, offset_y: int = 0):
        self.target_type = target_type
        self.anchor_data = anchor_data
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.is_attached = True
        logger.info(f"[WindowAttachment] Attached window '{self.window_id}' to target '{target_type}'")

    def detach(self):
        self.is_attached = False
        self.is_following = False
        logger.info(f"[WindowAttachment] Detached window '{self.window_id}'")

    def move(self, new_x: int, new_y: int) -> Tuple[int, int]:
        self.offset_x = new_x
        self.offset_y = new_y
        return new_x, new_y

    def follow(self) -> bool:
        if self.is_attached:
            self.is_following = True
            logger.info(f"[WindowAttachment] Window '{self.window_id}' is now following target '{self.target_type}'")
            return True
        return False

    def release(self):
        self.is_following = False

    def update_anchor(self, new_anchor_data: Dict[str, Any]) -> Tuple[int, int]:
        self.anchor_data = new_anchor_data
        ax = new_anchor_data.get("x", 0)
        ay = new_anchor_data.get("y", 0)
        aw = new_anchor_data.get("w", 0)
        
        nx = ax + aw + self.offset_x
        ny = ay + self.offset_y
        logger.info(f"[WindowAttachment] Updated anchor for '{self.window_id}': Position recalculated to ({nx}, {ny})")
        return nx, ny
