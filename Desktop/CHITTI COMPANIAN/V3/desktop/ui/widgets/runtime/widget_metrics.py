import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WidgetMetrics:
    """
    S36D-2: Metrics tracking active widgets, lazy instantiations, and render profile FPS targets.
    """
    def __init__(self):
        self.active_widget_count = 0
        self.lazy_instantiations = 0

    def record_widget_created(self):
        self.active_widget_count += 1
        self.lazy_instantiations += 1

    def record_widget_destroyed(self):
        self.active_widget_count = max(0, self.active_widget_count - 1)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "active_widgets": self.active_widget_count,
            "lazy_instantiations": self.lazy_instantiations,
            "render_fps_target": 30
        }
