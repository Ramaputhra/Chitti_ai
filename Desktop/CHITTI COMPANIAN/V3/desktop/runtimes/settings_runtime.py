import logging
import json
import os
from typing import Dict, Any, List, Optional

from desktop.models.lifecycle import IRuntime, HealthState
from desktop.app.context import KernelContext
from desktop.models.settings import PlatformSettings

logger = logging.getLogger(__name__)

class SettingsRuntime(IRuntime):
    """
    Manages platform settings defining HOW CHITTI behaves.
    Follows Rule 263: Configuration Ownership.
    """
    def __init__(self, config_dir: str = "AppData/CHITTI/settings"):
        self.context: Optional[KernelContext] = None
        self._running = False
        self._config_dir = config_dir
        self._settings = PlatformSettings()
        self._settings_file = os.path.join(self._config_dir, "settings.json")

    @property
    def dependencies(self) -> List[Any]:
        return []

    async def initialize(self, context: KernelContext) -> bool:
        self.context = context
        if not os.path.exists(self._config_dir):
            try:
                os.makedirs(self._config_dir, exist_ok=True)
            except Exception as e:
                logger.warning(f"Could not create settings dir: {e}")
        return True

    async def start(self) -> bool:
        self._running = True
        self.reload_settings()
        logger.info("SettingsRuntime started.")
        return True

    async def stop(self) -> bool:
        self._running = False
        return True

    def health(self) -> HealthState:
        return HealthState.HEALTHY

    async def shutdown(self) -> bool:
        return True

    def reload_settings(self):
        """Hot reloads settings from disk."""
        if os.path.exists(self._settings_file):
            try:
                with open(self._settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._settings = PlatformSettings.from_dict(data)
                    logger.info("Settings hot reloaded from disk.")
            except Exception as e:
                logger.error(f"Failed to load settings.json: {e}")
        else:
            self.save_settings() # Create default

    def save_settings(self):
        """Persists current settings to disk."""
        if not os.path.exists(self._config_dir):
            return
        try:
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings.to_dict(), f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save settings.json: {e}")

    @property
    def current(self) -> PlatformSettings:
        return self._settings
