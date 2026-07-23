from datetime import datetime
from typing import Dict, Any, List
from desktop.models.observation import Observation
import uuid

class BaseSource:
    def _create_observation(
        self,
        correlation_id: str,
        session_id: str,
        observation_type: str,
        payload: Dict[str, Any]
    ) -> Observation:
        return Observation(
            observation_id=str(uuid.uuid4()),
            correlation_id=correlation_id,
            session_id=session_id,
            observation_type=observation_type,
            timestamp=datetime.now(),
            source=self.__class__.__name__,
            payload=payload,
            confidence=1.0,
            source_reliability=1.0
        )

import os

class ProcessSource(BaseSource):
    APP_MAPPING = {
        "premiere.exe": {"name": "Adobe Premiere Pro", "activity": "Video Rendering", "category": "Media Production"},
        "adobe_premiere.exe": {"name": "Adobe Premiere Pro", "activity": "Video Rendering", "category": "Media Production"},
        "chrome.exe": {"name": "Google Chrome", "activity": "Browsing", "category": "Browser"},
        "msedge.exe": {"name": "Microsoft Edge", "activity": "Browsing", "category": "Browser"},
        "code.exe": {"name": "Visual Studio Code", "activity": "Software Development", "category": "IDE"},
        "devenv.exe": {"name": "Visual Studio", "activity": "Software Development", "category": "IDE"},
        "blender.exe": {"name": "Blender 3D", "activity": "3D Rendering", "category": "3D Modeling"},
        "obs64.exe": {"name": "OBS Studio", "activity": "Recording / Streaming", "category": "Broadcasting"},
        "obs.exe": {"name": "OBS Studio", "activity": "Recording / Streaming", "category": "Broadcasting"},
        "ffmpeg.exe": {"name": "FFmpeg Video Converter", "activity": "Video Encoding", "category": "Utility"}
    }

    def classify_process(self, exe_name: str) -> Dict[str, str]:
        """Maps raw executable process names to human-readable applications and user activities."""
        clean_name = exe_name.lower()
        if clean_name in self.APP_MAPPING:
            return self.APP_MAPPING[clean_name]
        return {"name": exe_name, "activity": "Background Process", "category": "General"}

    def observe_process(self, correlation_id: str, session_id: str, pid: int = None, name: str = None) -> List[Observation]:
        processes = [
            {"pid": 1001, "name": "notepad.exe", "parent_pid": 500, "cpu_percent": 0.1, "memory_mb": 15.0},
            {"pid": 1002, "name": "chrome.exe", "parent_pid": 500, "cpu_percent": 5.2, "memory_mb": 500.0},
            {"pid": 1003, "name": "premiere.exe", "parent_pid": 500, "cpu_percent": 82.0, "memory_mb": 4200.0},
            {"pid": 1004, "name": "code.exe", "parent_pid": 500, "cpu_percent": 3.1, "memory_mb": 350.0},
            {"pid": 1005, "name": "blender.exe", "parent_pid": 500, "cpu_percent": 91.0, "memory_mb": 6100.0},
            {"pid": 1006, "name": "obs64.exe", "parent_pid": 500, "cpu_percent": 12.5, "memory_mb": 450.0}
        ]
        results = []
        for p in processes:
            if (pid and p["pid"] == pid) or (name and p["name"] == name) or (not pid and not name):
                info = self.classify_process(p["name"])
                p["app_name"] = info["name"]
                p["user_activity"] = info["activity"]
                p["is_rendering"] = p["cpu_percent"] > 50.0 and ("Rendering" in info["activity"] or "Encoding" in info["activity"])
                results.append(self._create_observation(correlation_id, session_id, "process_state", p))
        return results

    def observe_application_intelligence(self, correlation_id: str, session_id: str) -> Observation:
        """Returns aggregated application intelligence & foreground activity mapping."""
        processes = self.observe_process(correlation_id, session_id)
        active_activities = [obs.payload["user_activity"] for obs in processes if obs.payload["user_activity"] != "Background Process"]
        render_jobs = [obs.payload["app_name"] for obs in processes if obs.payload.get("is_rendering")]
        
        payload = {
            "foreground_activity": active_activities[0] if active_activities else "Idle",
            "active_user_activities": list(set(active_activities)),
            "active_render_jobs": render_jobs,
            "render_in_progress": len(render_jobs) > 0
        }
        return self._create_observation(correlation_id, session_id, "application_intelligence", payload)

class WindowSource(BaseSource):
    def observe_windows(self, correlation_id: str, session_id: str, pid: int = None) -> List[Observation]:
        windows = [
            {"hwnd": 1, "pid": 1001, "title": "Untitled - Notepad", "bounds": (0, 0, 800, 600), "state": "normal", "is_active": True},
            {"hwnd": 2, "pid": 1002, "title": "Google", "bounds": (100, 100, 1024, 768), "state": "normal", "is_active": False},
            {"hwnd": 3, "pid": 1002, "title": "Settings", "bounds": (0, 0, 0, 0), "state": "minimized", "is_active": False}
        ]
        results = []
        for w in windows:
            if pid is None or w["pid"] == pid:
                results.append(self._create_observation(correlation_id, session_id, "window_state", w))
        return results

class DesktopSource(BaseSource):
    def observe_desktop(self, correlation_id: str, session_id: str) -> Observation:
        payload = {
            "foreground_app": "notepad.exe",
            "monitor_layout": [{"id": 1, "resolution": "1920x1080", "primary": True}]
        }
        return self._create_observation(correlation_id, session_id, "desktop_state", payload)

class ClipboardSource(BaseSource):
    def observe_clipboard(self, correlation_id: str, session_id: str) -> Observation:
        payload = {
            "type": "text",
            "content": "Copied from web",
            "clipboard_timestamp": datetime.now().isoformat()
        }
        return self._create_observation(correlation_id, session_id, "clipboard_state", payload)

class FilesystemSource(BaseSource):
    def observe_file(self, correlation_id: str, session_id: str, filepath: str) -> Observation:
        payload = {
            "filepath": filepath,
            "exists": True,
            "size_bytes": 1024,
            "last_modified": datetime.now().isoformat()
        }
        return self._create_observation(correlation_id, session_id, "filesystem_state", payload)

    def observe_storage_intelligence(self, correlation_id: str, session_id: str) -> Observation:
        """Returns storage intelligence, disk summary, downloads usage, and low disk alerts."""
        total_gb = 512.0
        used_gb = 468.0
        free_gb = total_gb - used_gb
        free_percent = (free_gb / total_gb) * 100.0
        
        payload = {
            "drive": "C:",
            "total_gb": total_gb,
            "used_gb": used_gb,
            "free_gb": free_gb,
            "free_percent": round(free_percent, 2),
            "is_low_disk": free_percent < 10.0,
            "downloads_size_gb": 42.5,
            "largest_folders": [
                {"path": "C:\\Users\\User\\Downloads", "size_gb": 42.5},
                {"path": "C:\\Program Files", "size_gb": 85.0},
                {"path": "C:\\Users\\User\\Videos", "size_gb": 120.0}
            ],
            "duplicate_detection_compatibility": {
                "supported": True,
                "engine_version": "1.0-compatible"
            }
        }
        return self._create_observation(correlation_id, session_id, "storage_intelligence", payload)

