from typing import Any, Dict

class KnowledgeAPI:
    def query(self, *args, **kwargs) -> Any:
        pass

class StorageAPI:
    def read(self, *args, **kwargs) -> Any:
        pass
        
    def write(self, *args, **kwargs) -> Any:
        pass

class PresentationAPI:
    def create(self, *args, **kwargs) -> Any:
        pass

class CapabilityAPI:
    def find(self, *args, **kwargs) -> Any:
        pass

class SettingsAPI:
    def get(self, *args, **kwargs) -> Any:
        pass

class LoggingAPI:
    def info(self, message: str) -> None:
        pass
        
    def error(self, message: str) -> None:
        pass

class ComponentAPI:
    def list(self) -> Any:
        pass

class UserAPI:
    def get_profile(self) -> Dict[str, Any]:
        pass

class PlatformAPI:
    """
    Rule 284: Plugins communicate exclusively through Platform APIs.
    This exposes safe wrappers around the core runtimes, completely isolating
    the plugins from implementation details.
    """
    def __init__(self):
        self.knowledge = KnowledgeAPI()
        self.storage = StorageAPI()
        self.presentation = PresentationAPI()
        self.services = CapabilityAPI()
        self.settings = SettingsAPI()
        self.logging = LoggingAPI()
        self.components = ComponentAPI()
        self.user = UserAPI()
