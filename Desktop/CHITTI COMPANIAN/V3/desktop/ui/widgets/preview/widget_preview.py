import os
import sys
import logging

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if v3_root not in sys.path:
    sys.path.insert(0, v3_root)

from desktop.ui.widgets.runtime.widget_runtime import WidgetRuntime
from desktop.ui.widgets.preview.mock_session_provider import MockSessionProvider
from desktop.ui.widgets.registry.widget_manifest_schema import WidgetCategory

def run_widget_preview_studio():
    print("==========================================================")
    print("CHITTI V2 — DESKTOP WIDGET FRAMEWORK PREVIEW STUDIO")
    print("==========================================================\n")

    w_runtime = WidgetRuntime()
    w_runtime.start()

    sessions = MockSessionProvider.get_mock_sessions()

    print(f"[1/6] Binding {len(sessions)} Mock Sessions to Generic Widgets...")
    for idx, sess in enumerate(sessions, start=1):
        w_id = f"w_{sess.session_type.lower()}_{idx}"
        widget = w_runtime.create_widget(w_id, sess.session_type, sess)
        
        if idx % 2 == 0:
            widget.expand()
        if idx % 3 == 0:
            w_runtime.attach_widget_to_character(w_id, {"x": 1520, "y": 340, "w": 400, "h": 400}, mode="right")

        rendered = widget.render()
        first_line = rendered.splitlines()[0] if rendered else ""
        print(f"      [{idx:02d}/{len(sessions)}] {widget.widget_type:14s} -> ID: {w_id:20s} | Render: {first_line[:45]}...")

    print("\n[2/6] Testing Category Filtering & Category Lookup...")
    for cat in WidgetCategory:
        widgets_in_cat = w_runtime.widget_manager.registry.get_widgets_by_category(cat.value)
        print(f"      Category '{cat.value:13s}': {len(widgets_in_cat)} active widgets")

    print("\n[3/6] Testing Manifest Versioning & Compatibility...")
    mf = w_runtime.widget_manager.registry.get_manifest("Media")
    print(f"      Media Manifest Schema v{mf.manifest_version}, Widget Implementation v{mf.widget_version}, Category: {mf.category}")

    print("\n[4/6] Testing Hot Reload of Manifests and Assets...")
    reloaded = w_runtime.hot_reload()
    print(f"      Hot Reload success: {reloaded}")

    print("\n[5/6] Testing Lazy Instantiation and Metrics Summary...")
    metrics = w_runtime.widget_manager.metrics.get_summary()
    print(f"      Active Widgets: {metrics['active_widgets']}, Lazy Instantiations: {metrics['lazy_instantiations']}")

    w_runtime.stop()
    print("\n==========================================================")
    print("DESKTOP WIDGET PREVIEW STUDIO EXECUTED CLEANLY")
    print("==========================================================")

if __name__ == "__main__":
    run_widget_preview_studio()
