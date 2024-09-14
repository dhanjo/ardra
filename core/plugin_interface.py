class PluginInterface:
    def __init__(self):
        """Initialize the plugin."""
        pass

    def run(self, data):
        """
        Main execution method for the plugin. 
        This method should take `data` as an argument and perform the core functionality of the plugin.
        It should return the result of the operation.
        
        Args:
            data (dict): A dictionary of input data that the plugin will use for execution.
            
        Returns:
            Any: The result of the plugin's operation.
        """
        raise NotImplementedError("Plugins must implement the 'run' method.")

    def terminate(self):
        """
        Optional method to clean up resources after the plugin completes its execution.
        This method is called by the plugin manager after running the plugin.
        """
        pass
