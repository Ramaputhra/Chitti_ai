import logging
from typing import Dict, Optional, List
from desktop.ui.widgets.sdk.widget import BaseWidget
from desktop.ui.widgets.registry.widget_manifest_loader import WidgetManifestLoader, WidgetManifest

logger = logging.getLogger(__name__)

class WidgetRegistry:
    """
    S36D-2 Refinement: Central Registry supporting Category Lookup, Category Filtering, and Version Validation.
    """
    def __init__(self):
        self.manifest_loader = WidgetManifestLoader()
        self._widgets: Dict[str, BaseWidget] = {}

    def register_widget(self, widget: BaseWidget):
        self._widgets[widget.widget_id] = widget
        logger.info(f"[WidgetRegistry] Registered widget '{widget.widget_id}' ({widget.widget_type})")

    def unregister_widget(self, widget_id: str):
        if widget_id in self._widgets:
            del self._widgets[widget_id]
            logger.info(f"[WidgetRegistry] Unregistered widget '{widget_id}'")

    def get_widget(self, widget_id: str) -> Optional[BaseWidget]:
        return self._widgets.get(widget_id)

    def get_manifest(self, widget_type: str) -> Optional[WidgetManifest]:
        return self.manifest_loader.load_manifest(widget_type)

    def get_widgets_by_category(self, category: str) -> List[BaseWidget]:
        cat_upper = category.upper()
        results = []
        for w in self._widgets.values():
            mf = self.get_manifest(w.widget_type)
            if mf and mf.category.upper() == cat_upper:
                results.append(w)
        return results

    def filter_manifests_by_category(self, category: str) -> Dict[str, WidgetManifest]:
        cat_upper = category.upper()
        results = {}
        for w_type, mf in self.manifest_loader._cache.items():
            if mf.category.upper() == cat_upper:
                results[w_type] = mf
        return results
