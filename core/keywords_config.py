# core/keywords_config.py

# Keywords and corresponding plugins for the tool
keyword_plugin_map = {
    "subdomain": {
        "keywords": [
            "find subdomains", 
            "enumerate subdomains", 
            "subdomain search", 
            "list subdomains"
        ],
        "plugin": "subdomain",  # Matches 'SubdomainPlugin'
        "output_naming": "subdomain_output.json"
    },
    "portscan": {
        "keywords": [
            "find open ports", 
            "scan ports", 
            "run port scan", 
            "port scan", 
            "list open ports",
            "run tcp scan",
            "run syn scan",
            "run udp scan",
            "run ping",
            "run os scan",
            "version detection"
        ],
        "plugin": "portscan",  # Matches 'PortscanPlugin'
        "output_naming": "portscan_output.json"
    }
}
