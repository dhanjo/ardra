import re
from datetime import datetime
from core.plugin_manager import PluginManager
from core.memory_manager import add_to_memory, load_memory, save_tool_output_to_json, parse_output_from_json
from core.keywords_config import keyword_plugin_map
from core.spinner import Spinner  # Spinner for loading animation
import ollama  # Assuming you are using Ollama API for Llama 3.1

# Initialize plugin manager and discover plugins
plugin_manager = PluginManager()
plugin_manager.discover_plugins()

def detect_keyword_and_plugin(prompt):
    """
    Detects the keyword from the user input and matches it with the appropriate plugin.
    """
    for tool, config in keyword_plugin_map.items():
        keywords = config["keywords"]
        plugin = config["plugin"]

        if any(keyword in prompt.lower() for keyword in keywords):
            domain_match = re.search(r"(\S+\.\S+)", prompt)  # Capture the domain
            if domain_match:
                domain = domain_match.group(1)
                return plugin, domain
            else:
                return plugin, None
    return None, None


def interact_with_llama(prompt, tool_output=None):
    """
    Interact with Llama 3.1, passing tool history and the current context.
    """
    memory = load_memory()  # Load past outputs from memory

    prompt_with_history = "You are a cybersecurity assistant. Here's the history of tool outputs:\n"

    # Add historical tool outputs to the prompt
    for entry in memory["history"]:
        prompt_with_history += f"Tool: {entry['tool']}, Domain: {entry['domain']}, Output: {entry['output']}\n"

    prompt_with_history += f"\nUser input: {prompt}\n"

    if tool_output:
        prompt_with_history += f"Recent tool output: {tool_output}\n"

    # Send the prompt with context to Llama 3.1
    response = ollama.chat(model="llama3.1", messages=[{"role": "user", "content": prompt_with_history}])

    response_text = response.get("message", {}).get("content", "")
    return response_text


def interact_with_plugin(prompt):
    """
    Handles the interaction with plugins, displaying a spinner during long tasks.
    """
    spinner = Spinner()

    # Start the spinner before calling the plugin
    print(f"Processing your request: {prompt}")
    spinner.start()

    try:
        # Detect keyword and corresponding plugin for tool execution
        plugin, domain = detect_keyword_and_plugin(prompt)
        if plugin and domain:
            print(f"Executing {plugin} on domain {domain}...")
            result = plugin_manager.run_plugins(plugin, {"domain": domain})  # Run the tool
            save_tool_output_to_json(plugin, domain, result)  # Save tool output to JSON
            add_to_memory(plugin, domain, result)  # Add the result to memory
            llama_response = interact_with_llama(prompt, result)  # Get Llama's response based on memory
            return llama_response
        elif plugin:
            return f"Error: No domain or target specified for {plugin}."
        else:
            # No plugin detected, handle it as a normal interaction
            return interact_with_llama(prompt)
    finally:
        # Stop the spinner after task completion
        spinner.stop()


def chat_loop():
    """
    Main loop for continuous interaction with the user.
    """
    print("You can now interact with the assistant. Type 'exit' to end the chat.")

    while True:
        user_input = input("You: ")

        if user_input.lower() == 'exit':
            print("Exiting chat. Goodbye!")
            break

        result = interact_with_plugin(user_input)
        print(f"Assistant: {result}")


if __name__ == "__main__":
    chat_loop()
