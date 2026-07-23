import os
import json
import logging
from typing import Dict, Optional
from desktop.ui.widgets.registry.widget_manifest_schema import WidgetManifest, WidgetCategory

logger = logging.getLogger(__name__)

class WidgetManifestLoader:
    """
    S36D-2 Refinement: Loads, validates, and migrates Widget Manifest JSON files with Manifest Versioning and Widget Categories.
    """
    CATEGORY_MAPPING = {
        "media": WidgetCategory.MEDIA.value,
        "email": WidgetCategory.COMMUNICATION.value,
        "browser": WidgetCategory.COMMUNICATION.value,
        "reminder": WidgetCategory.PRODUCTIVITY.value,
        "alarm": WidgetCategory.PRODUCTIVITY.value,
        "productivity": WidgetCategory.PRODUCTIVITY.value,
        "presentation": WidgetCategory.PRESENTATION.value,
        "vision": WidgetCategory.VISION.value,
        "battery": WidgetCategory.SYSTEM.value,
        "system": WidgetCategory.SYSTEM.value,
        "clipboard": WidgetCategory.AUTOMATION.value,
        "download": WidgetCategory.AUTOMATION.value,
        "upload": WidgetCategory.AUTOMATION.value,
        "timer": WidgetCategory.UTILITY.value,
        "weather": WidgetCategory.UTILITY.value,
        "navigation": WidgetCategory.UTILITY.value,
        "printer": WidgetCategory.UTILITY.value
    }

    def __init__(self, manifests_dir: Optional[str] = None):
        if manifests_dir:
            self.manifests_dir = manifests_dir
        else:
            v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            self.manifests_dir = os.path.join(v3_root, "desktop", "ui", "widgets", "manifests")
        self._cache: Dict[str, WidgetManifest] = {}

    def load_manifest(self, widget_type: str) -> Optional[WidgetManifest]:
        key = widget_type.lower()
        if key in self._cache:
            return self._cache[key]

        path = os.path.join(self.manifests_dir, f"{key}.json")
        default_cat = self.CATEGORY_MAPPING.get(key, WidgetCategory.UTILITY.value)

        if not os.path.exists(path):
            mf = WidgetManifest(
                manifest_version="1.0.0",
                widget_version="1.0.0",
                widget_id=f"widget_{key}",
                display_name=f"{widget_type} Widget",
                category=default_cat,
                supported_runtime_sessions=[widget_type]
            )
            self._cache[key] = mf
            return mf

        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)

            # Legacy Manifest Migration
            if "manifest_version" not in raw:
                logger.info(f"[WidgetManifestLoader] Migrating legacy manifest for '{widget_type}' -> manifest_version='1.0.0'")
                raw["manifest_version"] = "1.0.0"
            if "widget_version" not in raw:
                raw["widget_version"] = raw.get("version", "1.0.0")
            if "category" not in raw:
                raw["category"] = default_cat

            mf = WidgetManifest(**raw)
            self._cache[key] = mf
            logger.info(f"[WidgetManifestLoader] Loaded manifest for '{widget_type}' (Manifest v{mf.manifest_version}, Widget v{mf.widget_version}, Category: {mf.category})")
            return mf
        except Exception as e:
            logger.error(f"[WidgetManifestLoader] Failed to load manifest for '{widget_type}': {e}")
            return None

    def hot_reload(self):
        self._cache.clear()
        logger.info("[WidgetManifestLoader] Manifest cache hot-reloaded cleanly.")
