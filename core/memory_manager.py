import os
import json
from datetime import datetime

MEMORY_FILE = os.path.join("outputs", "memory.json")

# Load past tool outputs from memory
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"history": []}

# Save memory back to the memory.json file in the outputs directory
def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

# Add a tool output to memory and save it persistently
def add_to_memory(tool_name, domain, output):
    memory = load_memory()
    memory["history"].append({
        "tool": tool_name,
        "domain": domain,
        "output": output,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_memory(memory)
    return memory

# Function to save tool output and append results if they already exist
def save_tool_output_to_json(tool_name, domain, output):
    """
    Save and append tool output to a JSON file in the outputs folder.
    If the domain and plugin already exist, append to the output.
    """
    output_dir = os.path.join(os.getcwd(), "outputs")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, f"results_{domain}.json")

    # Load existing data or initialize an empty list
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            data = json.load(f)
    else:
        data = []

    # Create a new entry for the domain
    new_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "plugin": tool_name,
        "domain": domain,
        "output": output
    }

    # Update or append the result for the domain
    data.append(new_entry)

    # Save the updated data back to the JSON file
    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Output saved to {output_file}")
    return output_file

# Parse the JSON output for the specified domain and tool name.
# If tool_name is None, show all results for the domain.
def parse_output_from_json(domain, tool_name=None):
    """
    Parse the JSON output for the specified domain and tool name.
    If tool_name is None, show all results for the domain.
    """
    output_dir = os.path.join(os.getcwd(), "outputs")
    output_file = os.path.join(output_dir, f"results_{domain}.json")

    if not os.path.exists(output_file):
        return f"No results found for {domain}."

    with open(output_file, "r") as f:
        data = json.load(f)

    results = []
    for entry in data:
        if tool_name is None or entry['plugin'].lower() == tool_name.lower():
            results.append(entry)

    if not results:
        return f"No results found for {domain} with the tool {tool_name}."

    # Format the results for output
    formatted_results = []
    for result in results:
        formatted_results.append(
            f"Time: {result['time']}\n"
            f"Plugin: {result['plugin']}\n"
            f"Domain: {result['domain']}\n"
            f"Output: {result['output']}\n"
            "-------------------------"
        )

    return "\n\n".join(formatted_results)
