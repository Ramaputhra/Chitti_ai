import os
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

@dataclass
class RuntimeSessionModel:
    session_id: str = "sess_runtime_001"
    runtime_type: str = "assistant"
    owner_capability: str = "general_assistant"
    current_state: str = "RUNNING"
    resume_supported: bool = True
    restore_token: str = "token_res_default"
    session_context: Dict[str, Any] = field(default_factory=lambda: {"progress": 1.0, "step": 1})

@dataclass
class PresenceMemoryData:
    platform_schema_version: str = "1.0.0"
    presence_memory_version: str = "2.0.0"
    last_position_x: int = 1520
    last_position_y: int = 340
    last_dock_edge: str = "right"
    last_monitor: int = 0
    last_window_scale: float = 1.0
    last_presence_state: str = "CHARACTER_WINDOW"
    last_presentation_x: int = 100
    last_presentation_y: int = 100
    last_widget_layout: str = "default"
    last_widget_visibility: bool = True
    active_runtime_session: Dict[str, Any] = field(default_factory=lambda: asdict(RuntimeSessionModel()))
    last_active_presentation: str = "none"
    last_conversation_state: str = "COMPLETED"
    last_wake_source: str = "wake_word"
    last_input_mode: str = "Wake Word"
    last_character_scale: float = 1.0
    last_dock_animation: str = "SPRING_DOCK"
    last_theme: str = "dark_fluent"
    last_motion_theme: str = "fluent_motion"
    last_screen_resolution: str = "1920x1080"
    last_dpi_scale: float = 1.0
    last_desktop_workspace: str = "workspace_1"
    last_restore_bounds: Dict[str, int] = field(default_factory=lambda: {"x": 1520, "y": 340, "w": 400, "h": 400})

class PresenceMemory:
    """
    S36B-R2-R2: Expanded Presence Memory with Explicit Schema Versioning,
    Session-Centric Restoration, and Input Source Tracking.
    Supports automatic legacy migration based on explicit schema version check.
    """
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = storage_path
        else:
            v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            self.storage_path = os.path.join(v3_root, "desktop", "character", "presence", "presence_memory.json")
        self.data = PresenceMemoryData()
        self.load()

    def load(self) -> bool:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)

                current_ver = raw.get("presence_memory_version", "1.0.0")
                migrated = False

                # Explicit Schema Version Migration
                if current_ver != "2.0.0":
                    logger.info(f"[PresenceMemory] Migrating legacy schema version '{current_ver}' -> '2.0.0'")
                    raw["platform_schema_version"] = "1.0.0"
                    raw["presence_memory_version"] = "2.0.0"

                    # Convert legacy last_active_capability string to active_runtime_session dict
                    if "last_active_capability" in raw and "active_runtime_session" not in raw:
                        legacy_cap = raw.pop("last_active_capability", "general_assistant")
                        raw["active_runtime_session"] = asdict(RuntimeSessionModel(owner_capability=legacy_cap))

                    if "last_input_mode" not in raw:
                        raw["last_input_mode"] = "Wake Word"

                    migrated = True

                # Fill defaults for any missing keys
                default_dict = asdict(PresenceMemoryData())
                for k, v in default_dict.items():
                    if k not in raw:
                        raw[k] = v
                        migrated = True

                self.data = PresenceMemoryData(**raw)

                if migrated:
                    self.save()

                logger.info(f"[PresenceMemory] Loaded presence memory (v{self.data.presence_memory_version}) from '{self.storage_path}'")
                return True
            except Exception as e:
                logger.error(f"[PresenceMemory] Failed to load presence memory: {e}")
        return False

    def save(self) -> bool:
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(asdict(self.data), f, indent=2)
            logger.info(f"[PresenceMemory] Saved presence memory to '{self.storage_path}'")
            return True
        except Exception as e:
            logger.error(f"[PresenceMemory] Failed to save presence memory: {e}")
            return False

    def update_input_mode(self, input_mode: str):
        valid_modes = [
            "Wake Word", "Global Hotkey", "Tray Icon", "Presence Dot", "Character Window",
            "Desktop Shortcut", "Automation", "Developer Console", "Presentation Controller", "API"
        ]
        if input_mode in valid_modes:
            self.data.last_input_mode = input_mode
            self.save()

    def update_position(self, x: int, y: int, dock_edge: str = "right"):
        self.data.last_position_x = x
        self.data.last_position_y = y
        self.data.last_dock_edge = dock_edge
        self.data.last_restore_bounds = {"x": x, "y": y, "w": 400, "h": 400}
        self.save()
