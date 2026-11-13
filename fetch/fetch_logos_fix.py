#!/usr/bin/env python3
import urllib.request
from pathlib import Path

OUT = Path("/home/moon/Projects/logo")
OUT.mkdir(parents=True, exist_ok=True)
SI = "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons"

ITEMS = [
    ("sonarqubeserver.svg", f"{SI}/sonarqubeserver.svg", "Simple Icons"),
    ("suricata.svg", "https://raw.githubusercontent.com/OISF/suricata/master/assets/logo.svg", "OISF/Suricata GitHub"),
    ("yara.svg", "https://raw.githubusercontent.com/VirusTotal/yara/master/docs/images/yara-logo.svg", "VirusTotal/YARA GitHub"),
    ("nuclei.svg", "https://raw.githubusercontent.com/projectdiscovery/nuclei-templates/main/.github/nuclei-logo.svg", "ProjectDiscovery nuclei-templates GitHub"),
    ("sqlmap.svg", "https://raw.githubusercontent.com/sqlmapproject/sqlmap/master/doc/images/sqlmap_logo.svg", "sqlmap GitHub"),
    ("mitre-attack.svg", "https://raw.githubusercontent.com/mitre-attack/attack-website/master/attack-theme/static/images/mitre_attack_logo.svg", "MITRE ATT&CK site repo"),
    ("zaproxy.svg", f"{SI}/zaproxy.svg", "Simple Icons"),
    ("powershell.svg", "https://raw.githubusercontent.com/PowerShell/PowerShell/master/assets/ps_black_64.svg", "PowerShell GitHub"),
    ("osquery.svg", "https://raw.githubusercontent.com/osquery/osquery/master/docs/img/logo-2.svg", "osquery GitHub"),
    ("zeek.svg", "https://raw.githubusercontent.com/zeek/zeek/master/doc/zeek-logo.svg", "Zeek GitHub"),
    ("nmap.svg", "https://raw.githubusercontent.com/nmap/nmap/master/docs/nmap-logo-256x256.svg", "nmap GitHub"),
]

def valid_file(path: Path):
    data = path.read_bytes()
    if len(data) < 50:
        return False, f"too small ({len(data)}b)"
    head = data[:512].lstrip().lower()
    if path.suffix == '.svg':
        if b'<svg' not in head and b'<?xml' not in head:
            return False, 'not svg/xml'
    elif path.suffix == '.png':
        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            return False, 'not png'
    return True, f"ok {len(data)}b"

results = []
for name, url, note in ITEMS:
    dest = OUT / name
    if dest.exists():
        ok, msg = valid_file(dest)
        if ok:
            results.append((name, "EXISTS", msg, url, note))
            continue
        dest.unlink(missing_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"logo-fetcher/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        dest.write_bytes(data)
        ok, msg = valid_file(dest)
        if not ok:
            dest.unlink(missing_ok=True)
            results.append((name, "FAIL", f"invalid: {msg}", url, note))
        else:
            results.append((name, "DOWNLOADED", msg, url, note))
    except Exception as e:
        results.append((name, "FAIL", str(e), url, note))

ok_count = sum(1 for r in results if r[1] in ("DOWNLOADED","EXISTS"))
print(f"TOTAL_OK={ok_count}")
for r in results:
    print("|".join([r[0], r[1], r[2], r[3], r[4]]))
