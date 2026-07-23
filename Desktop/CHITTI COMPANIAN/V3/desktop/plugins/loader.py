"""
CHITTI Plugin System - Loader

Dynamic plugin loading and hot-reloading support.
"""
from typing import Dict, List, Optional, Type, Any
import logging
import importlib
import os
import json
from pathlib import Path

from desktop.plugins.base import (
    IPlugin, PluginMetadata, PluginConfig, PluginType,
    BasePlugin, PluginState
)
from desktop.plugins.registry import PluginRegistry, get_plugin_registry

logger = logging.getLogger(__name__)


class PluginLoader:
    """
    Handles dynamic loading of plugins from various sources.
    Supports:
    - File-based plugins (Python modules in directories)
    - Hot-reloading of plugins during development
    - Plugin configuration persistence
    """
    
    def __init__(
        self,
        registry: Optional[PluginRegistry] = None,
        plugin_dirs: Optional[List[str]] = None,
        config_dir: Optional[str] = None
    ):
        self.registry = registry or get_plugin_registry()
        self.plugin_dirs = plugin_dirs or []
        self.config_dir = config_dir or os.path.expanduser("~/.chitti/plugins")
        self._watched_files: Dict[str, float] = {}
        self._config_file = os.path.join(self.config_dir, "plugins.json")
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
    
    def discover_plugins(self) -> List[str]:
        """Discover all available plugins in plugin directories."""
        discovered = []
        
        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                continue
            
            for entry in os.listdir(plugin_dir):
                entry_path = os.path.join(plugin_dir, entry)
                
                # Check if it's a Python package
                if os.path.isdir(entry_path):
                    init_file = os.path.join(entry_path, "__init__.py")
                    if os.path.exists(init_file):
                        discovered.append(entry)
                
                # Check if it's a single file plugin
                elif entry.endswith(".py") and entry != "__init__.py":
                    module_name = entry[:-3]
                    discovered.append(module_name)
        
        return discovered
    
    def load_plugin_from_module(self, module_path: str) -> Optional[Type[IPlugin]]:
        """
        Load a plugin class from a module path.
        
        Args:
            module_path: Dotted module path (e.g., 'my_plugins.calculator')
        
        Returns:
            The plugin class if found, None otherwise.
        """
        try:
            module = importlib.import_module(module_path)
            
            # Look for plugin classes
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr != BasePlugin:
                    logger.info(f"Found plugin class: {attr_name} in {module_path}")
                    return attr
            
            logger.warning(f"No plugin class found in {module_path}")
            return None
            
        except ImportError as e:
            logger.error(f"Failed to import {module_path}: {e}")
            return None
    
    def load_plugin_from_file(self, file_path: str) -> Optional[Type[IPlugin]]:
        """Load a plugin from a Python file."""
        module_name = os.path.basename(file_path)[:-3]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        
        if not spec or not spec.loader:
            return None
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Look for plugin classes
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr != BasePlugin:
                return attr
        
        return None
    
    def install_plugin(
        self,
        source: str,
        plugin_id: Optional[str] = None
    ) -> bool:
        """
        Install a plugin from source.
        
        Args:
            source: File path, module path, or git URL
            plugin_id: Optional plugin ID for directory plugins
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Handle directory installation
            if os.path.isdir(source):
                return self._install_from_directory(source, plugin_id)
            
            # Handle file installation
            elif os.path.isfile(source):
                return self._install_from_file(source)
            
            # Handle module installation
            else:
                return self._install_from_module(source)
                
        except Exception as e:
            logger.error(f"Failed to install plugin from {source}: {e}")
            return False
    
    def _install_from_directory(self, source_dir: str, plugin_id: Optional[str]) -> bool:
        """Install a plugin from a directory."""
        if not plugin_id:
            plugin_id = os.path.basename(source_dir)
        
        target_dir = os.path.join(self.config_dir, "plugins", plugin_id)
        
        # Copy plugin files
        import shutil
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        
        shutil.copytree(source_dir, target_dir)
        
        # Load the plugin
        plugin_class = self.load_plugin_from_file(
            os.path.join(target_dir, "__init__.py")
        )
        
        if plugin_class:
            self.registry.register_plugin(plugin_class)
            return True
        
        return False
    
    def _install_from_file(self, source_file: str) -> bool:
        """Install a plugin from a Python file."""
        plugin_class = self.load_plugin_from_file(source_file)
        
        if plugin_class:
            self.registry.register_plugin(plugin_class)
            return True
        
        return False
    
    def _install_from_module(self, module_path: str) -> bool:
        """Install a plugin from a Python module."""
        plugin_class = self.load_plugin_from_module(module_path)
        
        if plugin_class:
            self.registry.register_plugin(plugin_class)
            return True
        
        return False
    
    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin."""
        target_dir = os.path.join(self.config_dir, "plugins", plugin_id)
        
        if os.path.exists(target_dir):
            import shutil
            shutil.rmtree(target_dir)
        
        return self.registry.unregister_plugin(plugin_id)
    
    def save_config(self) -> None:
        """Save plugin configuration to disk."""
        config = {
            "plugin_dirs": self.plugin_dirs,
            "plugins": {}
        }
        
        for plugin_id, metadata in [
            (m.id, m) for m in self.registry.list_plugins()
        ]:
            config["plugins"][plugin_id] = {
                "enabled": plugin_id in self.registry._enabled_plugins,
                "version": metadata.version
            }
        
        with open(self._config_file, "w") as f:
            json.dump(config, f, indent=2)
    
    def load_config(self) -> Dict[str, Any]:
        """Load plugin configuration from disk."""
        if not os.path.exists(self._config_file):
            return {}
        
        with open(self._config_file, "r") as f:
            return json.load(f)
    
    def check_for_updates(self) -> List[str]:
        """Check for plugin updates (files changed since last load)."""
        updated = []
        
        for file_path, last_mtime in self._watched_files.items():
            if not os.path.exists(file_path):
                continue
            
            current_mtime = os.path.getmtime(file_path)
            if current_mtime > last_mtime:
                updated.append(file_path)
        
        return updated
    
    def reload_plugin(self, plugin_id: str) -> bool:
        """Hot-reload a plugin."""
        plugin = self.registry.get_plugin(plugin_id)
        if not plugin:
            return False
        
        # Get current state
        metadata = self.registry.get_plugin_metadata(plugin_id)
        
        # Disable and unload
        self.registry.disable_plugin(plugin_id)
        self.registry.unload_plugin(plugin_id)
        
        # Reload module
        plugin_class = self.load_plugin_from_module(f"chitti_plugins.{plugin_id}")
        if not plugin_class:
            logger.error(f"Failed to reload plugin {plugin_id}")
            return False
        
        # Re-register and load
        self.registry.register_plugin(plugin_class)
        if self.registry.load_plugin(plugin_id):
            self.registry.enable_plugin(plugin_id)
            return True
        
        return False
    
    def watch_file(self, file_path: str) -> None:
        """Add a file to the watch list for hot-reloading."""
        if os.path.exists(file_path):
            self._watched_files[file_path] = os.path.getmtime(file_path)
    
    def watch_directory(self, directory: str) -> None:
        """Watch all Python files in a directory."""
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    self.watch_file(os.path.join(root, file))


# Example plugin template
PLUGIN_TEMPLATE = '''"""
{plugin_name} - CHITTI Plugin

{description}
"""
from typing import List, Dict, Any
from desktop.plugins.base import (
    BasePlugin, PluginMetadata, PluginType, PluginConfig
)


class {class_name}(BasePlugin):
    """{plugin_description}"""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id="{plugin_id}",
            name="{plugin_name}",
            version="1.0.0",
            author="{author}",
            description="{description}",
            plugin_type=PluginType.CAPABILITY,
            permissions=["capability.read"]
        )
    
    def on_load(self) -> bool:
        # Initialize plugin resources
        return super().on_load()
    
    def on_unload(self) -> bool:
        # Cleanup plugin resources
        return super().on_unload()
    
    def on_enable(self) -> None:
        super().on_enable()
        # Plugin-specific enable logic
    
    def on_disable(self) -> None:
        # Plugin-specific disable logic
        super().on_disable()


def get_plugin_class():
    """Factory function for plugin loading."""
    return {class_name}
'''


def create_plugin_template(
    plugin_id: str,
    plugin_name: str,
    description: str,
    author: str = "CHITTI User",
    output_dir: str = "."
) -> str:
    """Create a plugin template file."""
    class_name = "".join(word.title() for word in plugin_id.split("_")) + "Plugin"
    
    content = PLUGIN_TEMPLATE.format(
        plugin_name=plugin_name,
        class_name=class_name,
        plugin_id=plugin_id,
        description=description,
        author=author,
        plugin_description=description
    )
    
    output_path = os.path.join(output_dir, f"{plugin_id}.py")
    
    with open(output_path, "w") as f:
        f.write(content)
    
    return output_path
