# CHITTI Plugin SDK Documentation

Welcome to the CHITTI Plugin SDK! This guide will help you create plugins to extend CHITTI's capabilities.

## 🎯 Quick Start

```bash
# Install the CHITTI plugin template generator
pip install chitti-sdk

# Create a new plugin
chitti plugin create my-plugin --template capability
```

## 📦 Plugin Types

CHITTI supports 4 types of plugins:

### 1. Capability Plugin
Adds new tools/capabilities to CHITTI.

```python
from chitti.plugins import BasePlugin, PluginMetadata, PluginType

class MyCapabilityPlugin(BasePlugin):
    metadata = PluginMetadata(
        name="my-capability",
        version="1.0.0",
        author="Your Name",
        description="Does something amazing",
        plugin_type=PluginType.CAPABILITY
    )
    
    def get_tools(self):
        return [
            {
                "name": "my_tool",
                "description": "Does something",
                "parameters": {...}
            }
        ]
    
    def execute(self, tool_name, parameters):
        # Implement your tool logic
        return {"result": "success"}
```

### 2. Event Handler Plugin
Listens to and responds to events.

```python
class MyEventHandlerPlugin(BasePlugin):
    metadata = PluginMetadata(
        name="my-event-handler",
        version="1.0.0",
        author="Your Name",
        description="Handles events",
        plugin_type=PluginType.EVENT_HANDLER
    )
    
    def on_event(self, event):
        if event.type == "SPECIFIC_EVENT":
            return self.handle_specific_event(event)
        return None
```

### 3. Command Extension Plugin
Adds new voice commands or shortcuts.

```python
class MyCommandPlugin(BasePlugin):
    metadata = PluginMetadata(
        name="my-commands",
        version="1.0.0",
        author="Your Name",
        description="Adds commands",
        plugin_type=PluginType.COMMAND_EXTENSION
    )
    
    def get_commands(self):
        return [
            {
                "trigger": "hey chitti, do the thing",
                "action": "my_capability.do_thing"
            }
        ]
```

### 4. Integration Plugin
Connects to external services.

```python
class MyIntegrationPlugin(BasePlugin):
    metadata = PluginMetadata(
        name="my-integration",
        version="1.0.0",
        author="Your Name",
        description="Integrates with MyService",
        plugin_type=PluginType.INTEGRATION,
        config_schema={...}
    )
    
    def connect(self, config):
        # Initialize connection to external service
        self.client = MyServiceClient(config)
    
    def get_status(self):
        return self.client.is_connected()
```

## 🛠️ Plugin Structure

```
my_plugin/
├── __init__.py          # Plugin entry point
├── plugin.json          # Plugin metadata
├── capabilities/       # Capability implementations
├── handlers/           # Event handlers
├── commands/           # Command definitions
└── tests/              # Plugin tests
```

## 📄 plugin.json Schema

```json
{
    "name": "my-plugin",
    "version": "1.0.0",
    "author": "Your Name",
    "description": "What this plugin does",
    "type": "capability|event_handler|command_extension|integration",
    "requires": ["other_plugin>=1.0.0"],
    "conflicts": ["conflicting_plugin"],
    "permissions": ["microphone", "internet"],
    "config": {
        "api_key": {"type": "string", "required": true}
    }
}
```

## 🔧 Plugin API

### BasePlugin Methods

```python
class BasePlugin:
    metadata: PluginMetadata      # Plugin info
    config: dict                 # Plugin configuration
    
    def initialize(self) -> None:
        """Called when plugin loads."""
        pass
    
    def shutdown(self) -> None:
        """Called when plugin unloads."""
        pass
    
    def get_tools(self) -> List[dict]:
        """Return list of tools this plugin provides."""
        return []
    
    def get_settings(self) -> dict:
        """Return plugin settings schema."""
        return {}
    
    def validate_config(self, config: dict) -> bool:
        """Validate plugin configuration."""
        return True
```

### Logging

```python
from chitti.plugins import get_logger

logger = get_logger(__name__)

logger.info("Plugin started")
logger.warning("Something might be wrong")
logger.error("An error occurred")
```

### Storage

```python
from chitti.plugins import get_storage

storage = get_storage("my_plugin")

# Store data
storage.set("key", {"data": "value"})

# Retrieve data
data = storage.get("key")

# Delete data
storage.delete("key")
```

### Configuration

```python
from chitti.plugins import get_config

config = get_config()

# Get value
value = config.get("my_plugin.setting", default="default")

# Set value
config.set("my_plugin.setting", value)
```

## 🧪 Testing Your Plugin

```python
import pytest
from chitti.plugins.testing import PluginTestCase

class TestMyPlugin(PluginTestCase):
    plugin_class = MyPlugin
    
    def test_initialization(self):
        plugin = self.create_plugin()
        assert plugin.is_initialized()
    
    def test_tool_execution(self):
        plugin = self.create_plugin()
        result = plugin.execute("my_tool", {})
        assert result["status"] == "success"
```

## 📤 Publishing Your Plugin

### Step 1: Package Your Plugin

```bash
# Create distribution
python -m build
```

### Step 2: Create a Marketplace Listing

```bash
chitti marketplace publish --plugin ./dist/my_plugin-1.0.0.tar.gz
```

### Step 3: Share Your Plugin

Share your plugin on:
- CHITTI Marketplace
- GitHub
- PyPI

## 🔐 Security Considerations

1. **Permissions**: Only request necessary permissions
2. **Data Handling**: Never store sensitive data without encryption
3. **API Keys**: Use CHITTI's secure storage for secrets
4. **Input Validation**: Always validate user input

## 📚 Examples

### Example: Notion Integration Plugin

See `docs/examples/notion_plugin/` for a complete example.

### Example: Custom Voice Command Plugin

See `docs/examples/custom_commands/` for a complete example.

## 🆘 Support

- GitHub Issues: https://github.com/Ramaputhra/Chitti_ai/issues
- Discord: https://discord.gg/chitti
- Email: support@chitti.ai

---

**Happy Plugin Building!** 🚀
