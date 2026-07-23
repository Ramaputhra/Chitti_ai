import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

class DockingEngine:
    """
    S36D-1: Docking Engine consuming Character Anchor API & Screen Edge Anchors.
    Desktop UI Runtime SHALL consume Character Anchor API ONLY. Desktop UI Runtime SHALL NEVER move Character Window directly.
    """
    def calculate_character_attached_position(self, anchor: Dict[str, int], window_w: int, window_h: int, mode: str = "right") -> Tuple[int, int]:
        ax = anchor.get("x", 1520)
        ay = anchor.get("y", 340)
        aw = anchor.get("w", 400)
        ah = anchor.get("h", 400)

        if mode == "right":
            nx = ax + aw + 10
            ny = ay
        elif mode == "left":
            nx = max(0, ax - window_w - 10)
            ny = ay
        elif mode == "below":
            nx = ax
            ny = ay + ah + 10
        else:
            nx = ax + aw + 20
            ny = ay + 20

        logger.info(f"[DockingEngine] Calculated Character-Attached Position ({mode}) from Anchor ({ax}, {ay}): ({nx}, {ny})")
        return nx, ny
