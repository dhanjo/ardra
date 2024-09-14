# core/command_config.py

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
        "plugin": "subdomain"  # Matches 'SubdomainPlugin'
    },
    "show open ports of": {
        "regex": r"show open ports of (\S+)",
        "action": parse_output_from_json,
        "args": ["domain"],
        "plugin": "portscan"  # Changed to match 'PortscanPlugin'
    },
    "perform (\w+) scan on": {
        "regex": r"perform (\w+) scan on (\S+)(?: ports? ([\d,\s-]+))?",
        "action": None,  # Handled by the plugin
        "args": ["scan_type", "domain", "ports"],
        "plugin": "portscan"  # Changed to match 'PortscanPlugin'
    },
    "scan (\S+) with (\w+) scan": {
        "regex": r"scan (\S+) with (\w+) scan(?: ports? ([\d,\s-]+))?",
        "action": None,
        "args": ["domain", "scan_type", "ports"],
        "plugin": "portscan"  # Changed to match 'PortscanPlugin'
    },
    # Add more command mappings here as needed
}
