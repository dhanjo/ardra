# ardra.py

import re
from datetime import datetime
from core.plugin_manager import PluginManager
from core.memory_manager import add_to_memory, load_memory, save_tool_output_to_json, parse_output_from_json
from core.keywords_config import keyword_plugin_map
from core.command_config import command_map
from core.spinner import Spinner  # Spinner for loading animation
import ollama  # Assuming you are using Ollama API for Llama 3.1

# Initialize plugin manager and discover plugins
plugin_manager = PluginManager()
plugin_manager.discover_plugins()

def parse_user_input(prompt):
    """
    Parses the user input using keyword_config and command_config.
    Returns the action, plugin name, domain, and parameters dictionary.
    """
    action = None
    plugin_name = None
    domain = None
    parameters = {}

    # Check against command_map first
    for command, config in command_map.items():
        regex = config["regex"]
        match = re.search(regex, prompt, re.IGNORECASE)
        if match:
            action = config["action"]
            plugin_name = config["plugin"]
            args = config["args"]
            # Extract parameters based on args
            for i, arg in enumerate(args):
                value = match.group(i + 1) if i + 1 <= match.lastindex else None
                if arg == "ports" and value:
                    parameters[arg] = value.strip().replace(' ', '')
                else:
                    parameters[arg] = value
            domain = parameters.get("domain")
            return action, plugin_name, domain, parameters

    # If no command matches, check against keywords
    for tool, config in keyword_plugin_map.items():
        keywords = config["keywords"]
        if any(keyword in prompt.lower() for keyword in keywords):
            action = "run_plugin"
            plugin_name = config["plugin"]
            # Extract domain
            domain_match = re.search(r"(\b(?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b|\b\d{1,3}(?:\.\d{1,3}){3}\b)", prompt.lower())
            domain = domain_match.group(1) if domain_match else None
            parameters['domain'] = domain

            # Extract scan type
            if 'syn scan' in prompt.lower():
                parameters['scan_type'] = 'syn'
            elif 'tcp scan' in prompt.lower():
                parameters['scan_type'] = 'tcp'
            elif 'udp scan' in prompt.lower():
                parameters['scan_type'] = 'udp'
            elif 'ping scan' in prompt.lower():
                parameters['scan_type'] = 'ping'
            
            # Check for OS detection
            if 'os detection' in prompt.lower() or 'os scan' in prompt.lower():
                parameters['os_detection'] = True

            # Check for version detection
            if 'version detection' in prompt.lower() or 'version scan' in prompt.lower():
                parameters['version_detection'] = True

            # Extract ports
            ports_match = re.search(r'ports?\s+([\d,\s\-]+)', prompt.lower())
            if ports_match:
                parameters['ports'] = ports_match.group(1).strip().replace(' ', '')
            
            return action, plugin_name, domain, parameters

    # If no plugin or command is detected
    return None, None, None, None

def interact_with_llama(prompt, tool_output=None):
    """
    Interact with Llama 3.1, passing tool history and the current context.
    """
    memory = load_memory()  # Load past outputs from memory

    prompt_with_history = "You are a cybersecurity assistant. Here's the history of tool outputs:\n"

    # Add historical tool outputs to the prompt
    for entry in memory.get("history", []):
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
    Handles the interaction with plugins and actions, displaying a spinner during long tasks.
    """
    spinner = Spinner()

    # Start the spinner before processing
    print(f"Processing your request: {prompt}")
    spinner.start()

    try:
        # Parse user prompt to detect action, plugin, domain, and parameters
        action, plugin_name, domain, parameters = parse_user_input(prompt)
        
        if action == "run_plugin" and plugin_name and domain:
            print(f"Executing {plugin_name} on domain {domain} with parameters {parameters}...")
            result = plugin_manager.run_plugins(plugin_name, parameters)  # Run the tool with parameters
            
            if not result:
                return "Error: No output from the plugin."

            # Save the tool output to a JSON file (for both subdomain and portscan)
            save_tool_output_to_json(plugin_name, domain, result)  # Save tool output to JSON
            add_to_memory(plugin_name, domain, result)  # Add the result to memory
            llama_response = interact_with_llama(prompt, result)  # Get Llama's response based on memory
            return llama_response

        elif action == "parse_output" and domain:
            print(f"Retrieving and analyzing results for domain {domain}...")
            tool_name = None  # Retrieve all tools; alternatively, specify if needed
            # Identify which tool to parse based on the command
            for command, config in command_map.items():
                if re.match(config["regex"], prompt, re.IGNORECASE):
                    tool_name = config["plugin"]  # e.g., "subdomain" or "portscan"
                    break
            if tool_name:
                analysis = parse_output_from_json(domain, tool_name)
                return analysis
            else:
                return f"Error: Could not determine which tool's results to parse for {domain}."

        else:
            # No plugin or action detected, handle it as a normal interaction
            return interact_with_llama(prompt)

    except Exception as e:
        return f"Error: {str(e)}"
    
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
