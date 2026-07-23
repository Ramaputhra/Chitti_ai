"""
CHITTI Plugin Template Generator

Usage:
    python -m desktop.plugins.sdk.template_generator create <plugin_name> [--type capability]
    python -m desktop.plugins.sdk.template_generator list-templates
"""
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime


TEMPLATES = {
    "capability": {
        "description": "Add new tools/capabilities",
        "files": {
            "__init__.py": '''"""My Plugin - Capability Plugin."""
from desktop.plugins.base import BasePlugin, PluginMetadata, PluginType

class MyPlugin(BasePlugin):
    metadata = PluginMetadata(
        name="my_plugin",
        version="1.0.0",
        author="",
        description="",
        plugin_type=PluginType.CAPABILITY
    )
    
    def initialize(self):
        """Initialize the plugin."""
        pass
    
    def get_tools(self):
        """Return list of tools."""
        return [
            {
                "name": "my_tool",
                "description": "Does something useful",
                "parameters": {
                    "param1": {"type": "string", "required": True}
                }
            }
        ]
    
    def execute(self, tool_name, parameters):
        """Execute a tool."""
        if tool_name == "my_tool":
            return self.my_tool(**parameters)
        return {"error": f"Unknown tool: {tool_name}"}
    
    def my_tool(self, param1):
        """Your tool implementation."""
        return {"result": f"Processed: {param1}"}
''',
            "plugin.json": '''{
    "name": "my_plugin",
    "version": "1.0.0",
    "author": "",
    "description": "",
    "type": "capability",
    "chitti_version": ">=3.0.0",
    "permissions": []
}'''
        }
    },
    "event_handler": {
        "description": "Handle events and notifications",
        "files": {
            "__init__.py": '''"""My Event Handler Plugin."""
from desktop.plugins.base import BasePlugin, PluginMetadata, PluginType

class MyEventHandler(BasePlugin):
    metadata = PluginMetadata(
        name="my_event_handler",
        version="1.0.0",
        author="",
        description="",
        plugin_type=PluginType.EVENT_HANDLER
    )
    
    def initialize(self):
        """Subscribe to events."""
        self.subscribe("USER_SPEECH", self.on_user_speech)
        self.subscribe("MEETING_STARTED", self.on_meeting_started)
    
    def on_user_speech(self, event):
        """Handle user speech events."""
        return {"handled": True}
    
    def on_meeting_started(self, event):
        """Handle meeting started events."""
        return {"handled": True}
''',
            "plugin.json": '''{
    "name": "my_event_handler",
    "version": "1.0.0",
    "author": "",
    "description": "",
    "type": "event_handler",
    "chitti_version": ">=3.0.0",
    "permissions": []
}'''
        }
    },
    "integration": {
        "description": "Connect to external services",
        "files": {
            "__init__.py": '''"""My Integration Plugin."""
from desktop.plugins.base import BasePlugin, PluginMetadata, PluginType

class MyIntegration(BasePlugin):
    metadata = PluginMetadata(
        name="my_integration",
        version="1.0.0",
        author="",
        description="",
        plugin_type=PluginType.INTEGRATION,
        config_schema={
            "api_key": {"type": "string", "required": True},
            "service_url": {"type": "string", "required": True}
        }
    )
    
    def initialize(self):
        """Initialize the integration."""
        self.client = None
    
    def connect(self, config):
        """Connect to external service."""
        self.client = MyServiceClient(
            api_key=config["api_key"],
            url=config["service_url"]
        )
        return self.client.is_connected()
    
    def get_status(self):
        """Return connection status."""
        if self.client:
            return {"connected": self.client.is_connected()}
        return {"connected": False}
    
    def disconnect(self):
        """Disconnect from service."""
        if self.client:
            self.client.disconnect()
            self.client = None
''',
            "plugin.json": '''{
    "name": "my_integration",
    "version": "1.0.0",
    "author": "",
    "description": "",
    "type": "integration",
    "chitti_version": ">=3.0.0",
    "permissions": ["internet"],
    "config_schema": {
        "api_key": {"type": "string", "required": true},
        "service_url": {"type": "string", "required": true}
    }
}'''
        }
    },
    "command_extension": {
        "description": "Add custom voice commands",
        "files": {
            "__init__.py": '''"""My Command Extension Plugin."""
from desktop.plugins.base import BasePlugin, PluginMetadata, PluginType

class MyCommands(BasePlugin):
    metadata = PluginMetadata(
        name="my_commands",
        version="1.0.0",
        author="",
        description="",
        plugin_type=PluginType.COMMAND_EXTENSION
    )
    
    def get_commands(self):
        """Return list of command mappings."""
        return [
            {
                "trigger": "hey chitti, do the thing",
                "action": "my_plugin.do_thing",
                "description": "Does the thing"
            },
            {
                "trigger": "hey chitti, another action",
                "action": "my_plugin.another_action",
                "description": "Does another thing"
            }
        ]
    
    def do_thing(self):
        """Action handler."""
        return {"result": "Thing done!"}
    
    def another_action(self):
        """Another action handler."""
        return {"result": "Another action done!"}
''',
            "plugin.json": '''{
    "name": "my_commands",
    "version": "1.0.0",
    "author": "",
    "description": "",
    "type": "command_extension",
    "chitti_version": ">=3.0.0",
    "permissions": []
}'''
        }
    }
}


def create_plugin(name: str, plugin_type: str = "capability"):
    """Create a new plugin from template."""
    
    if plugin_type not in TEMPLATES:
        print(f"Error: Unknown plugin type: {plugin_type}")
        print(f"Available types: {', '.join(TEMPLATES.keys())}")
        return False
    
    template = TEMPLATES[plugin_type]
    
    # Create plugin directory
    plugin_dir = Path(f"plugins/{name}")
    plugin_dir.mkdir(parents=True, exist_ok=True)
    
    # Create files from template
    for filename, content in template["files"].items():
        filepath = plugin_dir / filename
        
        # Replace placeholder names
        content = content.replace("my_plugin", name.replace("-", "_"))
        content = content.replace("MyPlugin", name.replace("-", "_").title().replace("_", ""))
        content = content.replace("My Plugin", name.replace("-", " ").title())
        
        filepath.write_text(content)
        print(f"Created: {filepath}")
    
    # Create tests directory
    tests_dir = plugin_dir / "tests"
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / "__init__.py").write_text('"""Plugin tests."""')
    
    # Create README
    readme = f'''# {name.replace("_", " ").title()}

A CHITTI plugin.

## Installation

```bash
# Local development
python -m chitti plugin install ./{plugin_dir}

# Publish to marketplace
chitti marketplace publish
```

## Configuration

Configure in CHITTI settings under Plugins > {name}.

## Development

```bash
# Test locally
python -m pytest tests/

# Build
python -m build
```
'''
    (plugin_dir / "README.md").write_text(readme)
    print(f"Created: {plugin_dir / 'README.md'}")
    
    print(f"\n✅ Plugin '{name}' created successfully!")
    print(f"\n📁 Location: {plugin_dir}")
    print(f"🔧 Type: {plugin_type}")
    print("\n📝 Next steps:")
    print(f"   1. cd {plugin_dir}")
    print("   2. Edit plugin.json with your details")
    print("   3. Implement your plugin logic")
    print("   4. Add tests in tests/")
    print("   5. Test with: python -m chitti plugin test")
    
    return True


def list_templates():
    """List available plugin templates."""
    print("\n📦 Available Plugin Templates:\n")
    print("-" * 60)
    
    for name, template in TEMPLATES.items():
        print(f"\n🔹 {name.upper()}")
        print(f"   {template['description']}")
        print(f"   Files: {', '.join(template['files'].keys())}")
    
    print("\n" + "-" * 60)
    print("\n💡 Usage:")
    print("   python -m desktop.plugins.sdk.template_generator create my-plugin --type capability")


def main():
    parser = argparse.ArgumentParser(description="CHITTI Plugin Generator")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new plugin")
    create_parser.add_argument("name", help="Plugin name")
    create_parser.add_argument("--type", "-t", default="capability",
                             choices=list(TEMPLATES.keys()),
                             help="Plugin type")
    
    # List command
    subparsers.add_parser("list-templates", help="List available templates")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_plugin(args.name, args.type)
    elif args.command == "list-templates":
        list_templates()
    else:
        parser.print_help()
        list_templates()


if __name__ == "__main__":
    main()
