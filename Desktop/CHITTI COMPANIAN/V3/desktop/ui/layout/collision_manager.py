import logging
from typing import List, Tuple
from desktop.ui.window.transparent_window import TransparentWindow

logger = logging.getLogger(__name__)

class CollisionManager:
    """
    S36D-1: Collision Detection & Edge Avoidance Manager.
    """
    def check_collision(self, win1: TransparentWindow, win2: TransparentWindow) -> bool:
        return not (
            win1.x + win1.width <= win2.x or
            win1.x >= win2.x + win2.width or
            win1.y + win1.height <= win2.y or
            win1.y >= win2.y + win2.height
        )

    def avoid_collisions(self, windows: List[TransparentWindow]):
        for i in range(len(windows)):
            for j in range(i + 1, len(windows)):
                if self.check_collision(windows[i], windows[j]):
                    logger.info(f"[CollisionManager] Collision detected between '{windows[i].window_id}' and '{windows[j].window_id}'. Resolving...")
                    windows[j].move(windows[j].x, windows[i].y + windows[i].height + 10)
