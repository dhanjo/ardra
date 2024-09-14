#!/usr/bin/env python3

import nmap
import os
from datetime import datetime

def run_nmap_scan(targets, ports=None, scan_type='syn', os_detection=False, version_detection=False, save_output=False, output_dir=None):
    """
    Perform an Nmap scan with the given parameters.
    After scanning, the result will be formatted and saved if requested.
    """
    try:
        # Initialize Nmap scanner
        scanner = nmap.PortScanner()

        # Build Nmap scan arguments
        args = ''
        if scan_type == 'syn':
            args += '-sS '
        elif scan_type == 'udp':
            args += '-sU '
        elif scan_type == 'tcp':
            args += '-sT '
        elif scan_type == 'ping':
            args += '-sn '
        else:
            args += '-sS '  # Default to SYN scan

        if os_detection:
            args += '-O '
        if version_detection:
            args += '-sV '
        if ports:
            args += f'-p {ports} '

        # Perform the scan
        scanner.scan(hosts=targets, arguments=args)

        # Collect scan results
        scan_results = scanner._scan_result  # Raw scan results as a dictionary

        # Format the scan results
        formatted_results = format_scan_results(scan_results)

        # Save output to a file if requested
        if save_output:
            if output_dir is None:
                output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
            save_scan_output(targets, formatted_results, output_dir)  # Save the formatted output

        # Return the formatted results
        return formatted_results

    except Exception as e:
        return f"Error: Unable to run Nmap scan. {str(e)}"

def save_scan_output(targets, formatted_output, output_dir):
    """
    Save the formatted Nmap scan output to a .txt file.
    """
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get current date and time
    current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Clean targets string for filename
    filename_targets = targets.replace('/', '_').replace(':', '_').replace(',', '_').replace(' ', '_')

    # Build filename
    output_filename = f"{filename_targets}_{current_date}.txt"
    output_path = os.path.join(output_dir, output_filename)

    # Save the formatted output to the file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(formatted_output)

    print(f"Formatted scan results saved to {output_path}")

def format_scan_results(scan_results):
    """
    Format the raw scan results into a human-readable string format.
    """
    output = ""
    if 'scan' not in scan_results or not scan_results['scan']:
        return "No scan results."

    for host, result in scan_results['scan'].items():
        output += f"\nHost: {host}\n"
        status = result.get('status', {}).get('state', 'unknown')
        output += f"Status: {status}\n"

        # Handle Open Ports
        protocols = ['tcp', 'udp']
        ports_found = False
        for proto in protocols:
            if proto in result:
                ports = result[proto]
                if ports:
                    ports_found = True
                    output += f"\nOpen {proto.upper()} Ports:\n"
                    for port, port_data in ports.items():
                        state = port_data.get('state', 'unknown')
                        service = port_data.get('name', 'unknown')
                        product = port_data.get('product', '')
                        version = port_data.get('version', '')
                        extrainfo = port_data.get('extrainfo', '')
                        output += f"  Port {port}: {state}\n"
                        output += f"    Service: {service}\n"
                        if product or version or extrainfo:
                            output += f"    Details: {product} {version} {extrainfo}\n"
        if not ports_found:
            output += "No open ports found.\n"

        # Handle OS detection (if enabled)
        if 'osmatch' in result:
            output += "\nOS Matches:\n"
            for os_match in result['osmatch']:
                output += f"  - {os_match['name']} ({os_match['accuracy']}% accuracy)\n"

    return output.strip()  # Remove any trailing whitespace


