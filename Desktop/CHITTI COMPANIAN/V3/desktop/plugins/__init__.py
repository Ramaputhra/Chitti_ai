"""
CHITTI Plugin System

Provides extensibility through a plugin architecture.
"""
from desktop.plugins.base import (
    IPlugin,
    ICapabilityPlugin,
    IEventHandlerPlugin,
    ICommandExtensionPlugin,
    IIntegrationPlugin,
    BasePlugin,
    PluginMetadata,
    PluginConfig,
    PluginState,
    PluginType,
)
from desktop.plugins.registry import (
    PluginRegistry,
    PluginRegistration,
    get_plugin_registry,
)
from desktop.plugins.loader import (
    PluginLoader,
    create_plugin_template,
)

__all__ = [
    # Base classes
    "IPlugin",
    "ICapabilityPlugin", 
    "IEventHandlerPlugin",
    "ICommandExtensionPlugin",
    "IIntegrationPlugin",
    "BasePlugin",
    # Models
    "PluginMetadata",
    "PluginConfig",
    "PluginState",
    "PluginType",
    # Registry
    "PluginRegistry",
    "PluginRegistration",
    "get_plugin_registry",
    # Loader
    "PluginLoader",
    "create_plugin_template",
]
