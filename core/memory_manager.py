# memory_management.py

import os
import json
from datetime import datetime
import re

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

    # Append the result for the domain
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
    If tool_name is None, show all results for the domain from both subdomain and portscan outputs.
    """
    output_dir = os.path.join(os.getcwd(), "outputs")
    tool_files = []

    if tool_name is None:
        # Include both subdomain and portscan output files
        tool_files = ["subdomain_output.json", "portscan_output.json"]
    else:
        # Map tool names to their respective output files
        tool_file_map = {
            "subdomain": "subdomain_output.json",
            "portscan": "portscan_output.json"
        }
        tool_file = tool_file_map.get(tool_name.lower())
        if tool_file:
            tool_files.append(tool_file)
        else:
            return f"No such tool: {tool_name}"

    all_results = []

    for file_name in tool_files:
        output_file = os.path.join(output_dir, file_name)
        if not os.path.exists(output_file):
            continue  # Skip if the file does not exist

        with open(output_file, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue  # Skip files with invalid JSON

        for entry in data:
            if entry.get("domain", "").lower() == domain.lower():
                if tool_name is None or entry.get("plugin", "").lower() == tool_name.lower():
                    all_results.append(entry)

    if not all_results:
        if tool_name:
            return f"No results found for {domain} with the tool {tool_name}."
        else:
            return f"No results found for {domain}."

    # Format the results for output
    formatted_results = []
    for result in all_results:
        plugin = result.get("plugin", "N/A").lower()
        output = result.get("output", {})
        
        if plugin == "portscan":
            # Parse the portscan output to extract open ports
            portscan_output = output.get("PortscanPlugin", "")
            open_ports = extract_open_ports(portscan_output)
            output_formatted = "\n".join([f"- Port {port} ({service})" for port, service in open_ports.items()])
        elif plugin == "subdomain":
            # Parse the subdomain output if needed
            subdomain_output = output.get("SubdomainPlugin", "")
            subdomains = extract_subdomains(subdomain_output)
            output_formatted = "\n".join([f"- {subdomain}" for subdomain in subdomains])
        else:
            # For other plugins, just dump the output
            output_formatted = json.dumps(output, indent=4)

        formatted_results.append(
            f"Time: {result.get('time', 'N/A')}\n"
            f"Plugin: {result.get('plugin', 'N/A')}\n"
            f"Domain: {result.get('domain', 'N/A')}\n"
            f"Output:\n{output_formatted}\n"
            "-------------------------"
        )

    return "\n\n".join(formatted_results)

def extract_open_ports(portscan_output):
    """
    Extract open ports and their services from the portscan output string.
    Returns a dictionary with port numbers as keys and services as values.
    """
    open_ports = {}
    # Example portscan_output:
    # "Host: 185.199.109.153\nStatus: up\n\nOpen TCP Ports:\n  Port 80: open\n    Service: http\n  Port 443: open\n    Service: https"
    lines = portscan_output.splitlines()
    for line in lines:
        port_match = re.match(r'\s*Port\s+(\d+):\s+open', line)
        service_match = re.match(r'\s*Service:\s+(\w+)', line)
        if port_match:
            port = port_match.group(1)
            current_port = port
        elif service_match and 'current_port' in locals():
            service = service_match.group(1)
            open_ports[current_port] = service
            del current_port  # Reset for next port
    return open_ports

def extract_subdomains(subdomain_output):
    """
    Extract subdomains from the subdomain output string.
    Returns a list of subdomains.
    """
    # Example subdomain_output:
    # "Subdomains for dhananjaygarg.com saved: ['admin.dhananjaygarg.com', 'mail.dhananjaygarg.com']"
    subdomains = []
    match = re.search(r"Subdomains for .*? saved: \[(.*?)\]", subdomain_output)
    if match:
        subdomains_str = match.group(1)
        subdomains = [sd.strip().strip("'").strip('"') for sd in subdomains_str.split(',')]
    return subdomains
