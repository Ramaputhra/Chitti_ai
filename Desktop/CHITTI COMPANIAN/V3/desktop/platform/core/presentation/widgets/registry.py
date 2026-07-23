from typing import Dict, Type
from desktop.platform.core.presentation.widgets.contracts import IWidgetRenderer

class WidgetRegistry:
    """
    Registry for business widgets so recipes request them by ID
    instead of instantiating classes directly.
    """
    def __init__(self):
        self._widgets: Dict[str, Type[IWidgetRenderer]] = {}

    def register(self, widget_id: str, widget_class: Type[IWidgetRenderer]):
        self._widgets[widget_id] = widget_class

    def get(self, widget_id: str) -> Type[IWidgetRenderer]:
        if widget_id not in self._widgets:
            raise KeyError(f"Widget {widget_id} not found in registry")
        return self._widgets[widget_id]

# Singleton
widget_registry = WidgetRegistry()
