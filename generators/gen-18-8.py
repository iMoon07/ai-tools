import json, re, pathlib

def block(title, columns, nodes, groups, facilities, caption):
    spec = {
        "title": title,
        "columns": columns,
        "nodes": nodes,
        "groups": groups,
        "facilities": facilities
    }
    js = json.dumps(spec, ensure_ascii=False, indent=2)
    return "```topology\n" + js + "\n```\n\n" + caption + "\n"

def n(label, sub, icon):
    return [label, sub, "security:" + icon, "tech"]

recon_nodes = {
    "nmap": n("Nmap", "Port scanner", "nmap"),
    "masscan": n("Masscan", "Fast scanner", "masscan"),
    "netdiscover": n("Netdiscover", "ARP sweep", "netdiscover"),
    "arping": n("Arping", "ARP ping", "arping"),
    "unicornscan": n("Unicornscan", "Async scanner", "unicornscan"),
    "hping3": n("Hping3", "Packet crafter", "hping3"),
    "thcping6": n("THC-ping6", "IPv6 ping", "thcping6"),
    "nbtscan": n("NBTscan", "NetBIOS scan", "nbtscan"),
    "amass": n("Amass", "Subdomain enum", "amass"),
    "dnsrecon": n("DNSRecon", "DNS enum", "dnsrecon"),
    "dnsenum": n("DNSEnum", "DNS brute", "dnsenum"),
    "dnsmap": n("DNSmap", "DNS brute", "dnsmap"),
    "fierce": n("Fierce", "DNS recon", "fierce"),
    "dmitry": n("Dmitry", "Host info", "dmitry"),
    "theharvester": n("theHarvester", "Email OSINT", "theharvester"),
    "spiderfoot": n("SpiderFoot", "OSINT automation", "spiderfoot"),
    "maltego": n("Maltego", "Link analysis", "maltego"),
    "recon-ng": n("recon-ng", "OSINT framework", "recon-ng"),
    "metagoofil": n("Metagoofil", "Metadata OSINT", "metagoofil"),
    "cewl": n("CeWL", "Wordlist gen", "cewl"),
    "wordlists": n("Wordlists", "Payload lists", "wordlists"),
    "eyewitness": n("EyeWitness", "Screenshot", "eyewitness"),
    "hashid": n("HashID", "Hash ID", "hashid"),
    "whatweb": n("WhatWeb", "Web fingerprint", "whatweb"),
    "wafw00f": n("WAFW00F", "WAF detect", "wafw00f"),
    "dirsearch": n("Dirsearch", "Path brute", "dirsearch"),
    "gobuster": n("Gobuster", "Path brute", "gobuster"),
    "ffuf": n("FFUF", "Fuzzer", "ffuf"),
    "wfuzz": n("WFuzz", "Fuzzer", "wfuzz"),
    "dirb": n("DirB", "Path brute", "dirb"),
}

recon_groups = [
    ["Discovery", ["nmap","masscan","netdiscover","arping","unicornscan","hping3","thcping6","nbtscan"], "crosshair"],
    ["DNS & OSINT", ["amass","dnsrecon","dnsenum","dnsmap","fierce","dmitry","theharvester"], "globe"],
    ["OSINT & web", ["spiderfoot","maltego","recon-ng","metagoofil","cewl","wordlists","eyewitness","hashid"], "scan"],
    ["Web enumeration", ["whatweb","wafw00f","dirsearch","gobuster","ffuf","wfuzz","dirb"], "terminal"],
]

exploit_nodes = {
    "metasploit": n("Metasploit", "Exploit framework", "metasploit"),
    "msfpc": n("MSFPC", "Payload maker", "msfpc"),
    "armitage": n("Armitage", "GUI framework", "armitage"),
    "covenant": n("Covenant", "C2 framework", "covenant"),
    "havoc": n("Havoc", "C2 framework", "havoc"),
    "starkiller": n("Starkiller", "C2 GUI", "starkiller"),
    "exploit-db": n("Exploit-DB", "Exploit index", "exploit-db"),
    "setoolkit": n("SET", "Social toolkit", "setoolkit"),
    "sqlmap": n("SQLMap", "SQL injection", "sqlmap"),
    "sqlninja": n("SQLNinja", "SQL injection", "sqlninja"),
    "sqlsus": n("SQLSUS", "SQL injection", "sqlsus"),
    "commix": n("Commix", "Command injection", "commix"),
    "w3af": n("W3AF", "Web auditor", "w3af"),
    "wapiti": n("Wapiti", "Web scanner", "wapiti"),
    "zaproxy": n("ZAP", "Web proxy", "zaproxy"),
    "webscarab": n("WebScarab", "Web proxy", "webscarab"),
    "burp": n("Burp", "Web proxy", "burp"),
    "burp-suite": n("Burp Suite", "Web proxy", "burp-suite"),
    "nikto": n("Nikto", "Web scanner", "nikto"),
    "skipfish": n("Skipfish", "Web scanner", "skipfish"),
    "wpscan": n("WPScan", "WordPress scan", "wpscan"),
    "jboss-autopwn": n("JBoss Autopwn", "JBoss exploit", "jboss-autopwn"),
    "davtest": n("DAVTest", "WebDAV test", "davtest"),
    "parsero": n("Parsero", "Robots parser", "parsero"),
    "shellter": n("Shellter", "AV evasion", "shellter"),
    "veil": n("Veil", "Payload evasion", "veil"),
    "backdoor-factory": n("Backdoor Factory", "Backdoor", "backdoor-factory"),
    "laudanum": n("Laudanum", "Web shell", "laudanum"),
    "weevely": n("Weevely", "Web shell", "weevely"),
    "webshells": n("WebShells", "Shell collection", "webshells"),
    "nishang": n("Nishang", "PowerShell", "nishang"),
    "powersploit": n("PowerSploit", "PowerShell", "powersploit"),
    "powershell-empire": n("Empire", "PowerShell C2", "powershell-empire"),
    "king-phisher-icon": n("King Phisher", "Phishing", "king-phisher-icon"),
    "beef-xss": n("Beef-XSS", "Browser hook", "beef-xss"),
}

exploit_groups = [
    ["Frameworks", ["metasploit","msfpc","armitage","covenant","havoc","starkiller","exploit-db","setoolkit"], "bug"],
    ["Web attacks", ["sqlmap","sqlninja","sqlsus","commix","w3af","wapiti","zaproxy","webscarab"], "globe"],
    ["Web scanners", ["burp","burp-suite","nikto","skipfish","wpscan","jboss-autopwn","davtest","parsero"], "scan"],
    ["Payloads", ["shellter","veil","backdoor-factory","laudanum","weevely","webshells","nishang","powersploit","powershell-empire","king-phisher-icon","beef-xss"], "terminal"],
]

post_nodes = {
    "mimikatz": n("Mimikatz", "Credential dump", "mimikatz"),
    "hashcat": n("Hashcat", "Password cracker", "hashcat"),
    "john": n("John", "Password cracker", "john"),
    "hydra": n("Hydra", "Login brute", "hydra"),
    "medusa": n("Medusa", "Login brute", "medusa"),
    "ncrack": n("Ncrack", "Login brute", "ncrack"),
    "patator": n("Patator", "Login brute", "patator"),
    "ophcrack": n("Ophcrack", "LM cracker", "ophcrack"),
    "impacket": n("Impacket", "Protocol toolkit", "impacket"),
    "responder": n("Responder", "LLMNR poison", "responder"),
    "crackmapexec": n("CrackMapExec", "Network exec", "crackmapexec"),
    "evil-winrm": n("Evil-WinRM", "WinRM shell", "evil-winrm"),
    "bloodhound": n("BloodHound", "AD graph", "bloodhound"),
    "peass": n("PEASS", "Privesc scripts", "peass"),
    "unix-privesc-check": n("Unix Privesc", "Privesc check", "unix-privesc-check"),
    "chntpw": n("Chntpw", "Windows registry", "chntpw"),
    "rainbowcrack": n("RainbowCrack", "Rainbow tables", "rainbowcrack"),
    "rcracki-mt": n("Rcracki", "Rainbow tables", "rcracki-mt"),
    "pyrit": n("Pyrit", "WPA GPU", "pyrit"),
    "cowpatty": n("Cowpatty", "WPA capture", "cowpatty"),
    "samdump2": n("Samdump2", "SAM dump", "samdump2"),
    "hash-identifier": n("Hash Identifier", "Hash ID", "hash-identifier"),
    "hashit": n("Hashit", "Hash tool", "hashit"),
}

post_groups = [
    ["Credentials", ["mimikatz","hashcat","john","hydra","medusa","ncrack","patator","ophcrack"], "lock-keyhole"],
    ["Lateral movement", ["impacket","responder","crackmapexec","evil-winrm","bloodhound","peass","unix-privesc-check","chntpw"], "network"],
    ["Password attacks", ["rainbowcrack","rcracki-mt","pyrit","cowpatty","samdump2","hash-identifier","hashit"], "lock-keyhole"],
]

network_nodes = {
    "wireshark": n("Wireshark", "Packet capture", "wireshark"),
    "tcpdump": n("Tcpdump", "Packet capture", "tcpdump"),
    "ncat": n("Ncat", "Netcat", "ncat"),
    "netcat": n("Netcat", "Netcat", "netcat"),
    "dsniff": n("Dsniff", "Sniffing", "dsniff"),
    "ettercap": n("Ettercap", "MITM", "ettercap"),
    "bettercap": n("Bettercap", "MITM", "bettercap"),
    "mitmproxy": n("MITM Proxy", "Intercept", "mitmproxy"),
    "sslscan": n("SSLScan", "TLS scan", "sslscan"),
    "sslyze": n("SSLyze", "TLS scan", "sslyze"),
    "sslsplit": n("Sslsplit", "TLS MITM", "sslsplit"),
    "stunnel4": n("Stunnel", "TLS tunnel", "stunnel4"),
    "sslh": n("Sslh", "TLS demux", "sslh"),
    "iodine": n("Iodine", "DNS tunnel", "iodine"),
    "dns2tcp": n("Dns2tcp", "DNS tunnel", "dns2tcp"),
    "ptunnel": n("Ptunnel", "ICMP tunnel", "ptunnel"),
    "udptunnel": n("UDPTunnel", "UDP tunnel", "udptunnel"),
    "proxychains": n("Proxychains", "Proxy chain", "proxychains"),
    "proxytunnel": n("Proxytunnel", "Proxy tunnel", "proxytunnel"),
    "tor-browser": n("Tor Browser", "Anonymity", "tor-browser"),
    "openvpn": n("OpenVPN", "VPN", "openvpn"),
    "wireguard": n("WireGuard", "VPN", "wireguard"),
    "aircrack-ng": n("Aircrack-ng", "WiFi cracker", "aircrack-ng"),
    "reaver": n("Reaver", "WPS attack", "reaver"),
    "pixiewps": n("PixieWPS", "WPS attack", "pixiewps"),
    "wifite": n("Wifite", "WiFi automation", "wifite"),
    "fern-wifi-cracker": n("Fern", "WiFi cracker", "fern-wifi-cracker"),
    "bully": n("Bully", "WPS attack", "bully"),
    "mdk3": n("MDK3", "WiFi attack", "mdk3"),
    "kismet": n("Kismet", "WiFi IDS", "kismet"),
    "sparrow-wifi": n("Sparrow WiFi", "WiFi audit", "sparrow-wifi"),
    "airgeddon": n("Airgeddon", "WiFi framework", "airgeddon"),
}

network_groups = [
    ["Capture & MITM", ["wireshark","tcpdump","ncat","netcat","dsniff","ettercap","bettercap","mitmproxy"], "wifi"],
    ["TLS", ["sslscan","sslyze","sslsplit","stunnel4","sslh"], "lock-keyhole"],
    ["Tunnels & anonymity", ["iodine","dns2tcp","ptunnel","udptunnel","proxychains","proxytunnel","tor-browser","openvpn","wireguard"], "network"],
    ["Wireless", ["aircrack-ng","reaver","pixiewps","wifite","fern-wifi-cracker","bully","mdk3","kismet","sparrow-wifi","airgeddon"], "wifi"],
]

forensics_nodes = {
    "autopsy": n("Autopsy", "Disk forensics", "autopsy"),
    "volatility": n("Volatility", "Memory forensics", "volatility"),
    "binwalk": n("Binwalk", "Firmware analysis", "binwalk"),
    "foremost": n("Foremost", "File carving", "foremost"),
    "scalpel": n("Scalpel", "File carving", "scalpel"),
    "bulk-extractor": n("Bulk Extractor", "Artifact scan", "bulk-extractor"),
    "guymager": n("Guymager", "Disk imaging", "guymager"),
    "fls": n("FLS", "File listing", "fls"),
    "icat": n("ICAT", "File extract", "icat"),
    "mmls": n("MMLS", "Partition map", "mmls"),
    "mmstat": n("MMStat", "Partition stats", "mmstat"),
    "fsstat": n("FSStat", "FS stats", "fsstat"),
    "blkls": n("BLKLS", "Block listing", "blkls"),
    "blkcat": n("BLKCAT", "Block extract", "blkcat"),
    "blkcalc": n("BLKCALC", "Block calc", "blkcalc"),
    "istat": n("ISTAT", "Inode stats", "istat"),
    "radare2": n("Radare2", "RE framework", "radare2"),
    "cutter": n("Cutter", "RE GUI", "cutter"),
    "ghidra": n("Ghidra", "RE suite", "ghidra"),
    "jadx": n("JADX", "APK decompiler", "jadx"),
    "jd-gui": n("JD-GUI", "Java decompiler", "jd-gui"),
    "dex2jar": n("Dex2Jar", "APK converter", "dex2jar"),
    "bytecode-viewer": n("Bytecode Viewer", "APK analysis", "bytecode-viewer"),
    "ollydbg": n("OllyDbg", "Debugger", "ollydbg"),
    "apktool": n("APKTool", "APK reverse", "apktool"),
    "clamav": n("ClamAV", "AV scanner", "clamav"),
    "chkrootkit": n("Chkrootkit", "Rootkit check", "chkrootkit"),
    "rkhunter": n("RKHunter", "Rootkit check", "rkhunter"),
    "yara": n("YARA", "Pattern matching", "yara"),
    "virustotal": n("VirusTotal", "Malware scan", "virustotal"),
    "malwarebytes": n("Malwarebytes", "Malware scan", "malwarebytes"),
    "snort": n("Snort", "Network IDS", "snort"),
    "wazuh": n("Wazuh", "Security platform", "wazuh"),
}

forensics_groups = [
    ["Disk & memory", ["autopsy","volatility","binwalk","foremost","scalpel","bulk-extractor","guymager","fls"], "hard-drive"],
    ["File carving", ["icat","mmls","mmstat","fsstat","blkls","blkcat","blkcalc","istat"], "layers"],
    ["Reverse engineering", ["radare2","cutter","ghidra","jadx","jd-gui","dex2jar","bytecode-viewer","ollydbg","apktool"], "code"],
    ["Malware triage", ["clamav","chkrootkit","rkhunter","yara","virustotal","malwarebytes","snort","wazuh"], "bug"],
]

blocks = [
    ("Recon & enumeration", recon_nodes, recon_groups,
     "How to read: each column is a recon phase. Top to bottom, the tools move from network discovery to DNS/OSINT to web enumeration. Every node is a tool; the logo is from the local security catalogue."),
    ("Exploitation", exploit_nodes, exploit_groups,
     "How to read: each column is an exploitation phase. Frameworks launch, web tools attack web targets, scanners find issues, and payloads deliver. The groups label the phase; the footer repeats the security context."),
    ("Post-exploitation", post_nodes, post_groups,
     "How to read: each column is a post-exploitation phase. Credentials first, then lateral movement, password attacks, and wireless/MITM. Follow the group labels to keep the phases straight."),
    ("Forensics & reverse engineering", forensics_nodes, forensics_groups,
     "How to read: each column is an analysis phase. Disk artifacts, file carving, reverse engineering, and malware triage. Use the group labels to see which phase a tool belongs to."),
    ("Network & wireless", network_nodes, network_groups,
     "How to read: each column is a network phase. Capture and MITM first, then TLS, tunnels/anonymity, and wireless. The group labels keep the phases straight."),
]

parts = []
parts.append("### 18.8 Logo library — security tools\n\n")
parts.append("All 575 logos from `iMoon07/logo-svg` are available to every node (`\"logo\": \"security:nmap\"`). This section groups the security catalogue by hacking phase: recon, exploitation, post-exploitation, and forensics. Every node is a tool; the logo is the catalogue entry.\n\n")
for title, nodes, groups, caption in blocks:
    cols = [[nid for nid in group[1]] for group in groups]
    parts.append("#### " + title + "\n\n")
    parts.append(block(title, cols, nodes, groups, ["Security", ["shield", "Hacking toolkit"], ["terminal", "CLI first"]], caption))
    parts.append("\n")

new = "".join(parts)

p = pathlib.Path("/home/moon/Projects/Penjelajah-CyberSecurity/blog-post-template/template-for-you-en.md")
text = p.read_text()
start = text.index("### 18.8 Logo library")
end = text.index("## 19 — Topology Visual Lab")
text = text[:start] + new + text[end:]
p.write_text(text)
print("written", len(text))
