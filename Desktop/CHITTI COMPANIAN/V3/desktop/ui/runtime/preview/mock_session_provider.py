import logging
from typing import Dict, Any, List
from desktop.ui.runtime.widgets.base_widget import UISession

logger = logging.getLogger(__name__)

class MockSessionProvider:
    """
    S36D: Provides complete mock runtime sessions for all 16 generic widget types.
    """
    @staticmethod
    def get_mock_sessions() -> List[UISession]:
        return [
            UISession("sess_media_1", "Media", {"title": "Cyberpunk Synthwave", "artist": "CHITTI Beats", "playing": True, "progress": 0.45}),
            UISession("sess_reminder_1", "Reminder", {"title": "Engineering Review", "time_remaining": "10m", "completed": False}),
            UISession("sess_alarm_1", "Alarm", {"title": "Daily Standup", "countdown": "05:00"}),
            UISession("sess_navigation_1", "Navigation", {"destination": "Innovation Park", "eta": "14 mins", "distance": "5.2 km"}),
            UISession("sess_email_1", "Email", {"sender": "Engineering Lead", "subject": "Sprint Certification Approved", "unread_count": 3}),
            UISession("sess_download_1", "Download", {"filename": "chitti_v2_core.zip", "progress": 0.82, "eta": "5s"}),
            UISession("sess_upload_1", "Upload", {"filename": "telemetry_logs.tar.gz", "progress": 0.60, "eta": "12s"}),
            UISession("sess_presentation_1", "Presentation", {"name": "CHITTI Architecture Overview", "current_slide": 4, "total_slides": 12}),
            UISession("sess_vision_1", "Vision", {"camera_preview": "active", "ocr_status": "READY", "detection_count": 2}),
            UISession("sess_browser_1", "Browser", {"active_tab": "GitHub - CHITTI Companion", "url": "https://github.com/Ramaputhra"}),
            UISession("sess_printer_1", "Printer", {"printer": "Office HP LaserJet", "pages": 8, "status": "PRINTING"}),
            UISession("sess_clipboard_1", "Clipboard", {"content": "verify_s36d_desktop_ui_runtime.py", "item_count": 5}),
            UISession("sess_weather_1", "Weather", {"location": "San Francisco", "temp": "21°C", "condition": "Partly Cloudy"}),
            UISession("sess_battery_1", "Battery", {"level": "94%", "charging": True, "remaining": "4h 20m"}),
            UISession("sess_system_1", "System", {"cpu": "12%", "ram": "4.2 GB / 16 GB", "storage": "120 GB Free"}),
            UISession("sess_productivity_1", "Productivity", {"task": "EPIC 36 S36D Verification", "focus_time": "45m"})
        ]
