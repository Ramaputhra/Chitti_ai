"""
CHITTI Plugin System - Registry

Manages plugin registration, loading, and lifecycle.
"""
from typing import Dict, List, Optional, Type, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging
import importlib
import pkgutil
import os

from desktop.plugins.base import (
    IPlugin, PluginMetadata, PluginConfig, PluginState, PluginType,
    BasePlugin, ICapabilityPlugin, IEventHandlerPlugin, 
    ICommandExtensionPlugin, IIntegrationPlugin
)

logger = logging.getLogger(__name__)


@dataclass
class PluginRegistration:
    """Registration info for a plugin."""
    metadata: PluginMetadata
    plugin_class: Type[IPlugin]
    instance: Optional[IPlugin] = None
    config: PluginConfig = field(default_factory=PluginConfig)
    loaded_at: Optional[datetime] = None
    error: Optional[str] = None


class PluginRegistry:
    """
    Central registry for all CHITTI plugins.
    Manages plugin discovery, loading, and lifecycle.
    """
    
    def __init__(self):
        self._plugins: Dict[str, PluginRegistration] = {}
        self._enabled_plugins: List[str] = []
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._commands: Dict[str, Dict[str, Any]] = {}
        self._integrations: Dict[str, IIntegrationPlugin] = {}
        self._initialized = False
    
    @property
    def initialized(self) -> bool:
        return self._initialized
    
    def register_plugin(
        self,
        plugin_class: Type[IPlugin],
        config: Optional[PluginConfig] = None
    ) -> bool:
        """
        Register a plugin class with the registry.
        """
        try:
            # Create temporary instance to get metadata
            instance = plugin_class()
            metadata = instance.metadata
            
            if metadata.id in self._plugins:
                logger.warning(f"Plugin {metadata.id} already registered")
                return False
            
            registration = PluginRegistration(
                metadata=metadata,
                plugin_class=plugin_class,
                config=config or PluginConfig()
            )
            
            self._plugins[metadata.id] = registration
            logger.info(f"Registered plugin: {metadata.id} v{metadata.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register plugin: {e}")
            return False
    
    def unregister_plugin(self, plugin_id: str) -> bool:
        """Unregister a plugin."""
        if plugin_id not in self._plugins:
            return False
        
        reg = self._plugins[plugin_id]
        if reg.instance and reg.state == PluginState.RUNNING:
            reg.instance.on_disable()
            reg.instance.on_unload()
        
        del self._plugins[plugin_id]
        self._enabled_plugins.remove(plugin_id)
        logger.info(f"Unregistered plugin: {plugin_id}")
        return True
    
    def get_plugin(self, plugin_id: str) -> Optional[IPlugin]:
        """Get a plugin instance by ID."""
        reg = self._plugins.get(plugin_id)
        return reg.instance if reg else None
    
    def get_plugin_metadata(self, plugin_id: str) -> Optional[PluginMetadata]:
        """Get plugin metadata by ID."""
        reg = self._plugins.get(plugin_id)
        return reg.metadata if reg else None
    
    def list_plugins(
        self,
        plugin_type: Optional[PluginType] = None,
        enabled_only: bool = False
    ) -> List[PluginMetadata]:
        """List all registered plugins."""
        result = []
        for reg in self._plugins.values():
            if plugin_type and reg.metadata.plugin_type != plugin_type:
                continue
            if enabled_only and reg.metadata.id not in self._enabled_plugins:
                continue
            result.append(reg.metadata)
        return result
    
    def load_plugin(self, plugin_id: str) -> bool:
        """Load a plugin instance."""
        reg = self._plugins.get(plugin_id)
        if not reg:
            logger.error(f"Plugin not found: {plugin_id}")
            return False
        
        if reg.instance:
            logger.warning(f"Plugin already loaded: {plugin_id}")
            return True
        
        try:
            reg.instance = reg.plugin_class()
            reg.instance.set_config(reg.config)
            
            if not reg.instance.on_load():
                reg.error = "Load failed"
                return False
            
            reg.loaded_at = datetime.now()
            logger.info(f"Loaded plugin: {plugin_id}")
            return True
            
        except Exception as e:
            reg.error = str(e)
            logger.error(f"Failed to load plugin {plugin_id}: {e}")
            return False
    
    def load_all_plugins(self) -> Dict[str, bool]:
        """Load all registered plugins."""
        results = {}
        for plugin_id in self._plugins:
            results[plugin_id] = self.load_plugin(plugin_id)
        return results
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a loaded plugin."""
        reg = self._plugins.get(plugin_id)
        if not reg or not reg.instance:
            return False
        
        try:
            reg.instance.on_enable()
            if plugin_id not in self._enabled_plugins:
                self._enabled_plugins.append(plugin_id)
            
            # Register event handlers if applicable
            if isinstance(reg.instance, IEventHandlerPlugin):
                self._register_event_handlers(plugin_id, reg.instance)
            
            # Register commands if applicable
            if isinstance(reg.instance, ICommandExtensionPlugin):
                self._register_commands(plugin_id, reg.instance)
            
            logger.info(f"Enabled plugin: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable plugin {plugin_id}: {e}")
            return False
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin."""
        reg = self._plugins.get(plugin_id)
        if not reg or not reg.instance:
            return False
        
        try:
            reg.instance.on_disable()
            if plugin_id in self._enabled_plugins:
                self._enabled_plugins.remove(plugin_id)
            
            # Unregister handlers
            if plugin_id in self._event_handlers:
                del self._event_handlers[plugin_id]
            
            # Unregister commands
            self._unregister_commands(plugin_id)
            
            logger.info(f"Disabled plugin: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable plugin {plugin_id}: {e}")
            return False
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin completely."""
        if plugin_id in self._enabled_plugins:
            self.disable_plugin(plugin_id)
        
        reg = self._plugins.get(plugin_id)
        if not reg or not reg.instance:
            return False
        
        try:
            reg.instance.on_unload()
            reg.instance = None
            reg.loaded_at = None
            logger.info(f"Unloaded plugin: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_id}: {e}")
            return False
    
    def _register_event_handlers(self, plugin_id: str, handler: IEventHandlerPlugin):
        """Register event handlers from a plugin."""
        handlers = handler.get_event_handlers()
        self._event_handlers[plugin_id] = []
        
        for event_type, callback in handlers.items():
            if event_type not in self._event_handlers:
                self._event_handlers[event_type] = []
            self._event_handlers[event_type].append(callback)
            self._event_handlers[plugin_id].append(callback)
    
    def _register_commands(self, plugin_id: str, commands: ICommandExtensionPlugin):
        """Register commands from a plugin."""
        for cmd in commands.get_commands():
            cmd_id = cmd.get("id", cmd.get("name"))
            self._commands[cmd_id] = {
                **cmd,
                "plugin_id": plugin_id
            }
    
    def _unregister_commands(self, plugin_id: str):
        """Unregister commands from a plugin."""
        to_remove = [
            cmd_id for cmd_id, cmd in self._commands.items()
            if cmd.get("plugin_id") == plugin_id
        ]
        for cmd_id in to_remove:
            del self._commands[cmd_id]
    
    def dispatch_event(self, event_type: str, event_data: Any) -> None:
        """Dispatch an event to all registered handlers."""
        handlers = self._event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(event_data)
            except Exception as e:
                logger.error(f"Event handler error ({event_type}): {e}")
    
    async def execute_command(self, command: str, args: Dict[str, Any]) -> Any:
        """Execute a plugin command."""
        cmd_info = self._commands.get(command)
        if not cmd_info:
            raise ValueError(f"Unknown command: {command}")
        
        plugin_id = cmd_info.get("plugin_id")
        plugin = self.get_plugin(plugin_id)
        if not plugin or not isinstance(plugin, ICommandExtensionPlugin):
            raise RuntimeError(f"Plugin not available for command: {command}")
        
        return await plugin.execute_command(command, args)
    
    def get_capabilities(self) -> List[Any]:
        """Get all capabilities from capability plugins."""
        capabilities = []
        for plugin_id in self._enabled_plugins:
            plugin = self.get_plugin(plugin_id)
            if isinstance(plugin, ICapabilityPlugin):
                capabilities.extend(plugin.get_capabilities())
        return capabilities
    
    def get_integration(self, integration_type: str) -> Optional[IIntegrationPlugin]:
        """Get an integration plugin by type."""
        return self._integrations.get(integration_type)
    
    def discover_plugins(self, plugin_dir: str) -> List[str]:
        """Discover plugins in a directory."""
        discovered = []
        
        if not os.path.exists(plugin_dir):
            return discovered
        
        for _, name, is_pkg in pkgutil.iter_modules([plugin_dir]):
            if is_pkg:
                discovered.append(name)
        
        return discovered
    
    def initialize(self) -> None:
        """Initialize the plugin system."""
        self._initialized = True
        logger.info("Plugin registry initialized")
    
    def shutdown(self) -> None:
        """Shutdown all plugins and the registry."""
        for plugin_id in list(self._enabled_plugins):
            self.disable_plugin(plugin_id)
            self.unload_plugin(plugin_id)
        
        self._plugins.clear()
        self._enabled_plugins.clear()
        self._event_handlers.clear()
        self._commands.clear()
        self._initialized = False
        logger.info("Plugin registry shutdown")


# Global plugin registry instance
_plugin_registry: Optional[PluginRegistry] = None


def get_plugin_registry() -> PluginRegistry:
    """Get the global plugin registry."""
    global _plugin_registry
    if _plugin_registry is None:
        _plugin_registry = PluginRegistry()
    return _plugin_registry
