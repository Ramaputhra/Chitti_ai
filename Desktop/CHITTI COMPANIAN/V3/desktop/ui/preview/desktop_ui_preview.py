import os
import sys
import logging

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if v3_root not in sys.path:
    sys.path.insert(0, v3_root)

from desktop.ui.runtime.desktop_ui_runtime import DesktopUIRuntime

def run_preview_studio():
    print("==========================================================")
    print("CHITTI V2 — DESKTOP UI RUNTIME FOUNDATION PREVIEW STUDIO")
    print("==========================================================\n")

    runtime = DesktopUIRuntime()
    runtime.start()

    print("[1/5] Creating Generic Windows (Floating, Notification, Dialog, Overlay)...")
    w1 = runtime.create_window("win_float_1", "FloatingWindow", 200, 200, 320, 200)
    w2 = runtime.create_window("win_notif_1", "NotificationWindow", 1540, 40, 340, 120)
    w3 = runtime.create_window("win_dialog_1", "DialogWindow", 400, 300, 480, 300)
    w4 = runtime.create_window("win_overlay_1", "OverlayWindow", 0, 0, 1920, 1080)

    print("[2/5] Testing Character-Attached Position via Character Anchor API...")
    anchor = {"x": 1520, "y": 340, "w": 400, "h": 400}
    runtime.attach_window_to_character("win_float_1", anchor, mode="right")
    print(f"      Window 'win_float_1' attached to Character Anchor ({w1.x}, {w1.y}).")

    print("[3/5] Testing GPU Composition & Render Profiles...")
    frame = runtime.render_frame("win_float_1", profile="WIDGET")
    print(f"      Rendered frame: {frame}")

    print("[4/5] Testing Theme Switcher (Dark -> Light -> System)...")
    runtime.set_theme("Light")
    print(f"      Active theme: {runtime.controller.theme_manager.active_theme.name}")

    print("[5/5] Testing Asset & Theme Hot Reload...")
    reloaded = runtime.hot_reload()
    print(f"      Hot Reload success: {reloaded}")

    runtime.stop()
    print("\n==========================================================")
    print("DESKTOP UI PREVIEW STUDIO EXECUTED CLEANLY")
    print("==========================================================")

if __name__ == "__main__":
    run_preview_studio()
