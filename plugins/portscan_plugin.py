# plugins/portscan_plugin.py

import json
import os
from datetime import datetime
from core.plugin_interface import PluginInterface

class PortscanPlugin(PluginInterface):
    def __init__(self):
        print("PortScan Plugin Initiated.")

    def run(self, data):
        """
        Execute the Nmap scan and append the results to a single portscan_output.json file.
        """
        print(f"PortscanPlugin received data: {data}")  # Debugging statement
        domain = data.get("domain", "")
        scan_type = data.get("scan_type", "syn")  # Default to 'syn' scan
        ports = data.get("ports", None)  # Ports to scan
        os_detection = data.get("os_detection", False)  # OS detection flag
        version_detection = data.get("version_detection", False)  # Version detection flag

        if domain:
            try:
                # Import the run_nmap_scan function from nmap_scanner.py
                from tools.PortScan.nmap_scanner import run_nmap_scan

                # Perform the scan
                scan_result = run_nmap_scan(
                    targets=domain,
                    ports=ports,
                    scan_type=scan_type,
                    os_detection=os_detection,
                    version_detection=version_detection,
                    save_output=True,  # This will save the output to the output folder
                    output_dir=os.path.join(os.getcwd(), "tools", "PortScan", "output")
                )

                if "error" in scan_result:
                    return f"Error: {scan_result['error']}"

                # **Append the scan results to portscan_output.json**
                output_file_json = os.path.join(os.getcwd(), "outputs", "portscan_output.json")
                self.append_scan_results_to_json(output_file_json, domain, scan_result)

                return f"Port scan for {domain} completed and appended to {output_file_json}."
            except Exception as e:
                return f"Error: {str(e)}"
        else:
            return "Error: No domain provided for port scanning."

    def append_scan_results_to_json(self, json_file_path, domain, scan_results):
        """
        Append the scan results to the portscan_output.json file.
        """
        # Load the existing data from the JSON file, or initialize an empty list
        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as f:
                data = json.load(f)
        else:
            data = []

        # Create the new entry for the domain
        new_entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "plugin": "portscan",
            "domain": domain,
            "output": {
                "PortscanPlugin": scan_results
            }
        }

        # Append the new entry to the existing data
        data.append(new_entry)

        # Write the updated data back to the JSON file
        with open(json_file_path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def terminate(self):
        print("PortScan Plugin Terminated.")
