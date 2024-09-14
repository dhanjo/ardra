import importlib
import os

class PluginManager:
    def __init__(self, plugin_dir=None):
        """
        Initialize the plugin manager. By default, it will look for plugins in the
        `plugins` directory relative to the file where this code resides.
        """
        if plugin_dir is None:
            self.plugin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../plugins")
        else:
            self.plugin_dir = os.path.abspath(plugin_dir)

        self.plugins = []

    def discover_plugins(self):
        """Discover and load plugins from the plugin directory."""
        if not os.path.exists(self.plugin_dir):
            raise FileNotFoundError(f"Plugin directory '{self.plugin_dir}' does not exist.")
        
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                class_name = ''.join([word.capitalize() for word in module_name.split('_')])
                module = importlib.import_module(f"plugins.{module_name}")
                plugin_class = getattr(module, class_name)
                print(f"Discovered plugin: {plugin_class.__name__}")  # Add print statement
                self.plugins.append(plugin_class())

    def run_plugins(self, task, data):
        """
        Run all discovered plugins that match the task name.
        The `task` is expected to be part of the plugin's class name (in lowercase).
        """
        results = {}
        for plugin in self.plugins:
            if task in plugin.__class__.__name__.lower():
                print(f"Executing plugin: {plugin.__class__.__name__} for task: {task}")
                result = plugin.run(data)
                results[plugin.__class__.__name__] = result
            else:
                print(f"Plugin {plugin.__class__.__name__} does not match task: {task}")
        return results

    def terminate_plugins(self):
        """
        Terminate all plugins that have a 'terminate' method.
        This method allows plugins to clean up or close resources if needed.
        """
        for plugin in self.plugins:
            if hasattr(plugin, "terminate"):
                plugin.terminate()
