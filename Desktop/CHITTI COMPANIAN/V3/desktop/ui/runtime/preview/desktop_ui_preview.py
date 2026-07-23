import os
import sys
import logging

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if v3_root not in sys.path:
    sys.path.insert(0, v3_root)

from desktop.ui.runtime.managers.widget_manager import WidgetManager
from desktop.ui.runtime.preview.mock_session_provider import MockSessionProvider

def run_desktop_ui_preview():
    print("==========================================================")
    print("CHITTI V2 — DESKTOP UI PREVIEW STUDIO")
    print("==========================================================\n")

    wm = WidgetManager()
    sessions = MockSessionProvider.get_mock_sessions()

    print(f"---> Binding {len(sessions)} Mock Sessions to Generic Widgets...")
    for idx, sess in enumerate(sessions, start=1):
        w_id = f"w_{sess.session_type.lower()}_{idx}"
        widget = wm.create_widget(w_id, sess.session_type)
        wm.bind_session(w_id, sess)
        
        # Test expand / dock
        if idx % 2 == 0:
            widget.expand()
        if idx % 3 == 0:
            widget.dock("right")

        rendered = widget.render()
        first_line = rendered.splitlines()[0] if rendered else ""
        print(f"     [{idx:02d}/{len(sessions)}] {widget.widget_type:14s} -> ID: {w_id:20s} | Render: {first_line[:50]}...")

    print("\n==========================================================")
    print("DESKTOP UI PREVIEW COMPLETE")
    print("==========================================================")

if __name__ == "__main__":
    run_desktop_ui_preview()
