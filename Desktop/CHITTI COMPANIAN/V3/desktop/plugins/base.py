"""
CHITTI Plugin System - Base Classes

Defines the core plugin interface and base classes for CHITTI extensibility.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PluginType(str, Enum):
    """Types of plugins supported by CHITTI."""
    CAPABILITY = "capability"
    EVENT_HANDLER = "event_handler"
    COMMAND_EXTENSION = "command_extension"
    INTEGRATION = "integration"
    RENDERER = "renderer"
    SERVICE = "service"


class PluginState(str, Enum):
    """Lifecycle states of a plugin."""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNLOADING = "unloading"


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    id: str
    name: str
    version: str
    author: str = ""
    description: str = ""
    plugin_type: PluginType = PluginType.CAPABILITY
    dependencies: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    min_chitti_version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    homepage: str = ""
    license: str = "MIT"


@dataclass
class PluginConfig:
    """Configuration for a plugin instance."""
    enabled: bool = True
    priority: int = 100
    config: Dict[str, Any] = field(default_factory=dict)
    auto_start: bool = True


class IPlugin(ABC):
    """
    Base interface for all CHITTI plugins.
    All plugins must implement this interface.
    """
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return the plugin metadata."""
        pass
    
    @abstractmethod
    def on_load(self) -> bool:
        """
        Called when the plugin is loaded.
        Return True if successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def on_unload(self) -> bool:
        """
        Called when the plugin is unloaded.
        Return True if successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def on_enable(self) -> None:
        """Called when the plugin is enabled."""
        pass
    
    @abstractmethod
    def on_disable(self) -> None:
        """Called when the plugin is disabled."""
        pass
    
    def on_config_changed(self, config: Dict[str, Any]) -> None:
        """Called when plugin configuration changes."""
        pass


class ICapabilityPlugin(IPlugin):
    """
    Plugin that provides new capabilities to CHITTI.
    """
    
    @abstractmethod
    def get_capabilities(self) -> List[Any]:
        """Return list of capability instances provided by this plugin."""
        pass


class IEventHandlerPlugin(IPlugin):
    """
    Plugin that handles system events.
    """
    
    @abstractmethod
    def get_event_handlers(self) -> Dict[str, Callable]:
        """Return dict of event_type -> handler function."""
        pass


class ICommandExtensionPlugin(IPlugin):
    """
    Plugin that adds new commands or intent handlers.
    """
    
    @abstractmethod
    def get_commands(self) -> List[Dict[str, Any]]:
        """Return list of command definitions."""
        pass
    
    @abstractmethod
    async def execute_command(self, command: str, args: Dict[str, Any]) -> Any:
        """Execute a command provided by this plugin."""
        pass


class IIntegrationPlugin(IPlugin):
    """
    Plugin that provides integration with external services.
    """
    
    @abstractmethod
    def get_integration_type(self) -> str:
        """Return the type of integration (e.g., 'slack', 'github')."""
        pass
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the external service."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the external service."""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the connection is working."""
        pass


class BasePlugin(IPlugin):
    """
    Base implementation of IPlugin with common functionality.
    """
    
    def __init__(self):
        self._state = PluginState.UNLOADED
        self._config: Optional[PluginConfig] = None
        self._logger = logging.getLogger(self.__class__.__name__)
    
    @property
    def state(self) -> PluginState:
        return self._state
    
    @property
    def config(self) -> Optional[PluginConfig]:
        return self._config
    
    def set_config(self, config: PluginConfig) -> None:
        self._config = config
    
    def on_load(self) -> bool:
        try:
            self._state = PluginState.LOADED
            self._logger.info(f"Plugin {self.metadata.id} loaded")
            return True
        except Exception as e:
            self._logger.error(f"Failed to load plugin: {e}")
            self._state = PluginState.ERROR
            return False
    
    def on_unload(self) -> bool:
        try:
            self._state = PluginState.UNLOADED
            self._logger.info(f"Plugin {self.metadata.id} unloaded")
            return True
        except Exception as e:
            self._logger.error(f"Failed to unload plugin: {e}")
            return False
    
    def on_enable(self) -> None:
        self._state = PluginState.RUNNING
        self._logger.info(f"Plugin {self.metadata.id} enabled")
    
    def on_disable(self) -> None:
        self._state = PluginState.STOPPED
        self._logger.info(f"Plugin {self.metadata.id} disabled")
    
    def on_config_changed(self, config: Dict[str, Any]) -> None:
        self._logger.info(f"Plugin {self.metadata.id} config changed")
