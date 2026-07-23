from typing import List
from desktop.ui.widgets.sdk.widget_session import WidgetSession

class MockSessionProvider:
    """
    S36D-2: Provides complete mock Runtime Sessions for all 17 generic widget types.
    """
    @staticmethod
    def get_mock_sessions() -> List[WidgetSession]:
        return [
            WidgetSession("sess_media_1", "Media", "media_player", {"title": "Cyberpunk Synthwave", "artist": "CHITTI Beats", "playing": True, "provider": "Spotify", "progress": 0.45}),
            WidgetSession("sess_reminder_1", "Reminder", "reminder_assistant", {"title": "Engineering Architecture Review", "time_remaining": "10m", "completed": False}),
            WidgetSession("sess_alarm_1", "Alarm", "alarm_clock", {"title": "Daily Standup Alarm", "countdown": "05:00"}),
            WidgetSession("sess_timer_1", "Timer", "timer_assistant", {"title": "Focus Session", "countdown": "25:00", "running": True}),
            WidgetSession("sess_email_1", "Email", "email_assistant", {"sender": "Lead Architect", "subject": "Sprint Certification Approved", "unread_count": 3}),
            WidgetSession("sess_browser_1", "Browser", "browser_automation", {"active_tab": "GitHub - CHITTI Companion", "url": "https://github.com/Ramaputhra"}),
            WidgetSession("sess_navigation_1", "Navigation", "maps_assistant", {"destination": "Innovation Park", "eta": "14 mins", "distance": "5.2 km"}),
            WidgetSession("sess_presentation_1", "Presentation", "presentation_engine", {"name": "CHITTI Architecture Overview", "current_slide": 4, "total_slides": 12}),
            WidgetSession("sess_printer_1", "Printer", "print_service", {"printer": "Office HP LaserJet", "pages": 8, "status": "PRINTING"}),
            WidgetSession("sess_clipboard_1", "Clipboard", "clipboard_manager", {"content": "verify_s36d_2_widget_framework.py", "item_count": 5}),
            WidgetSession("sess_download_1", "Download", "download_manager", {"filename": "chitti_v2_core.zip", "progress": 0.82, "eta": "5s"}),
            WidgetSession("sess_upload_1", "Upload", "upload_manager", {"filename": "telemetry_logs.tar.gz", "progress": 0.60, "eta": "12s"}),
            WidgetSession("sess_battery_1", "Battery", "power_manager", {"level": "94%", "charging": True, "remaining": "4h 20m"}),
            WidgetSession("sess_weather_1", "Weather", "weather_service", {"location": "San Francisco", "temp": "21°C", "condition": "Partly Cloudy"}),
            WidgetSession("sess_vision_1", "Vision", "camera_service", {"camera_preview": "active", "ocr_status": "READY", "detection_count": 2}),
            WidgetSession("sess_productivity_1", "Productivity", "focus_tracker", {"task": "EPIC 36 S36D-2 Verification", "focus_time": "45m"}),
            WidgetSession("sess_system_1", "System", "system_monitor", {"cpu": "12%", "ram": "4.2 GB / 16 GB", "storage": "120 GB Free"})
        ]
