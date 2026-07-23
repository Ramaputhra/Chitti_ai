import json
import os
import threading
from typing import Any, Dict

from desktop.platform.configuration.events import SystemEvents
from desktop.platform.configuration.paths import USER_SETTINGS_FILE
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.settings import ISettingsManager


class SettingsManager(ISettingsManager):
    """
    Thread-safe, file-backed Settings Manager.
    Used for runtime preferences (volume, theme, preferred AI provider).
    """

    def __init__(self, event_bus: IEventBus, logger: ILoggingService) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self._lock = threading.RLock()
        self._settings: Dict[str, Any] = {}
        self._file_path = USER_SETTINGS_FILE

    def initialize(self) -> None:
        with self._lock:
            if os.path.exists(self._file_path):
                try:
                    with open(self._file_path, "r", encoding="utf-8") as f:
                        self._settings = json.load(f)
                    self.logger.info("Settings loaded from disk")
                except Exception as e:
                    self.logger.exception(e, module="SettingsManager", error="Failed to load settings")
            else:
                self._settings = {}
                self._save()

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=4)
        except Exception as e:
            self.logger.exception(e, module="SettingsManager", error="Failed to save settings")

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            old_value = self._settings.get(key)
            if old_value == value:
                return
            self._settings[key] = value
            self._save()

        self.logger.info(f"Setting updated: {key}")
        self.event_bus.publish(
            Event(
                event_id=SystemEvents.SETTINGS_CHANGED,
                source="SettingsManager",
                payload={"key": key, "old_value": old_value, "new_value": value},
            )
        )

    def has(self, key: str) -> bool:
        with self._lock:
            return key in self._settings
