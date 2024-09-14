from core.plugin_manager import PluginManager
from core.memory_manager import parse_output_from_json

# Initialize PluginManager
plugin_manager = PluginManager()
plugin_manager.discover_plugins()

# This is a dictionary mapping commands to specific actions or plugins.
command_map = {
    "show subdomains of": {
        "regex": r"show subdomains of (\S+)",
        "action": parse_output_from_json,
        "args": ["domain"],
        "plugin": "subdomain"
    }
    # Add more command mappings here as needed
}
