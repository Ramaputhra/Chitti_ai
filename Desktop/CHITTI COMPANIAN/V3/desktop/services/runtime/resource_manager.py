import os
import shutil
from typing import List

from desktop.platform.configuration.paths import APP_DATA_DIR
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.resource import IResourceManager, ResourceType


class ResourceManager(IResourceManager):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self.base_dir = APP_DATA_DIR
        self._paths = {
            ResourceType.MODEL: os.path.join(self.base_dir, "models"),
            ResourceType.ICON: os.path.join(self.base_dir, "icons"),
            ResourceType.THEME: os.path.join(self.base_dir, "themes"),
            ResourceType.PLUGIN: os.path.join(self.base_dir, "plugins"),
            ResourceType.AUDIO: os.path.join(self.base_dir, "audio"),
            ResourceType.IMAGE: os.path.join(self.base_dir, "images"),
            ResourceType.TEMP: os.path.join(self.base_dir, "temp"),
        }

    def initialize(self) -> None:
        for path in self._paths.values():
            os.makedirs(path, exist_ok=True)
        self.logger.info("ResourceManager initialized directory structures")

    def get_path(self, resource_type: ResourceType, filename: str) -> str:
        return os.path.join(self._paths[resource_type], filename)

    def list_resources(self, resource_type: ResourceType) -> List[str]:
        path = self._paths[resource_type]
        if not os.path.exists(path):
            return []
        return os.listdir(path)

    def clear_temp(self) -> None:
        temp_dir = self._paths[ResourceType.TEMP]
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                os.makedirs(temp_dir)
                self.logger.info("Temporary resources cleared")
            except Exception as e:
                self.logger.exception(e, module="ResourceManager", error="Failed to clear temp")
