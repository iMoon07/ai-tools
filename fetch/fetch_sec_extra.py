#!/usr/bin/env python3
import urllib.request
from pathlib import Path

OUT = Path("/home/moon/Projects/logo")
OUT.mkdir(parents=True, exist_ok=True)

# (filename, url, source_note)
ITEMS = [
    # WAF / ModSec / Wazuh / IDS-IPS / C2 - probe candidates
    ("wazuh.svg", "https://raw.githubusercontent.com/wazuh/wazuh-dashboard/master/public/assets/wazuh_logo.svg", "Wazuh dashboard GitHub"),
    ("wazuh.svg", "https://raw.githubusercontent.com/wazuh/wazuh-kibana-app/master/public/assets/wazuh_logo.svg", "Wazuh kibana app GitHub"),
    ("wazuh.svg", "https://raw.githubusercontent.com/wazuh/wazuh-dashboard-plugins/master/plugins/main/public/assets/wazuh_logo.svg", "Wazuh plugins GitHub"),
    ("modsecurity.svg", "https://raw.githubusercontent.com/owasp-modsecurity/ModSecurity/v3/master/others/modsec_logo.svg", "ModSecurity GitHub"),
    ("modsecurity.svg", "https://raw.githubusercontent.com/SpiderLabs/ModSecurity/v3/master/others/modsec_logo.svg", "ModSecurity (SpiderLabs) GitHub"),
    ("modsecurity.svg", "https://raw.githubusercontent.com/coreruleset/coreruleset/main/docs/images/crs-logo.svg", "OWASP CRS GitHub"),
    ("suricata.svg", "https://raw.githubusercontent.com/OISF/suricata/master/assets/suricata.svg", "OISF Suricata GitHub"),
    ("suricata.svg", "https://raw.githubusercontent.com/OISF/suricata/master/doc/images/suricata-logo.svg", "OISF Suricata GitHub"),
    ("suricata.svg", "https://raw.githubusercontent.com/OISF/suricata/master/doc/userguide/_static/suricata-logo.svg", "OISF Suricata GitHub"),
    ("suricata.png", "https://raw.githubusercontent.com/OISF/suricata/master/assets/logo.png", "OISF Suricata GitHub"),
    ("zeek.svg", "https://raw.githubusercontent.com/zeek/zeek/master/doc/logo/zeek-logo.svg", "Zeek GitHub"),
    ("zeek.svg", "https://raw.githubusercontent.com/zeek/zeek/master/doc/zeek-logo-blue.svg", "Zeek GitHub"),
    ("zeek.svg", "https://zeek.org/wp-content/uploads/2020/04/zeek-logo-blue.svg", "zeek.org"),
    ("ossec.svg", "https://raw.githubusercontent.com/ossec/ossec-hids/master/docs/logo.svg", "OSSEC GitHub"),
    ("sliver.svg", "https://raw.githubusercontent.com/BishopFox/sliver/master/docs/sliver-logo.svg", "Sliver (BishopFox) GitHub"),
    ("sliver.svg", "https://raw.githubusercontent.com/BishopFox/sliver/master/.github/images/sliver-logo.svg", "Sliver GitHub"),
    ("sliver.png", "https://raw.githubusercontent.com/BishopFox/sliver/master/docs/static/img/sliver-logo.png", "Sliver GitHub"),
    ("havoc.svg", "https://raw.githubusercontent.com/HavocFramework/Havoc/main/assets/Havoc.svg", "Havoc GitHub"),
    ("havoc.png", "https://raw.githubusercontent.com/HavocFramework/Havoc/main/assets/Havoc.png", "Havoc GitHub"),
    ("mythic.svg", "https://raw.githubusercontent.com/its-a-feature/Mythic/master/mythic-docker/src/MythicUI/src/assets/mythic.svg", "Mythic GitHub"),
    ("mythic.png", "https://raw.githubusercontent.com/its-a-feature/Mythic/master/mythic-docker/src/MythicUI/src/assets/mythic.png", "Mythic GitHub"),
    ("empire.svg", "https://raw.githubusercontent.com/BC-SECURITY/Empire/main/docs/images/empire.svg", "Empire GitHub"),
    ("empire.png", "https://raw.githubusercontent.com/BC-SECURITY/Empire/main/empire/server/common/empire.png", "Empire GitHub"),
    ("crowdsec.svg", "https://raw.githubusercontent.com/crowdsecurity/crowdsec/master/docs/assets/logo_crowdsec.svg", "CrowdSec GitHub"),
    ("crowdsec.svg", "https://raw.githubusercontent.com/crowdsecurity/crowdsec-docs/main/crowdsec-docs/static/img/crowdsec_logo.svg", "CrowdSec docs GitHub"),
    ("fail2ban.svg", "https://raw.githubusercontent.com/fail2ban/fail2ban/master/doc/fail2ban.logo.svg", "Fail2ban GitHub"),
    ("fail2ban.png", "https://raw.githubusercontent.com/fail2ban/fail2ban/master/doc/fail2ban-logo.png", "Fail2ban GitHub"),
    ("coraza.svg", "https://raw.githubusercontent.com/corazawaf/coraza/main/docs/logo.svg", "Coraza WAF GitHub"),
    ("coraza.svg", "https://raw.githubusercontent.com/corazawaf/coraza.io/main/static/images/logo.svg", "Coraza site GitHub"),
    ("openappsec.svg", "https://raw.githubusercontent.com/openappsec/openappsec/main/build/cloud/agents/logo.svg", "open-appsec GitHub"),
    ("openappsec.png", "https://raw.githubusercontent.com/openappsec/openappsec/main/images/logo.png", "open-appsec GitHub"),
    ("bunkerweb.svg", "https://raw.githubusercontent.com/bunkerity/bunkerweb/master/src/common/core/misc/files/logo.svg", "BunkerWeb GitHub"),
    ("bunkerweb.svg", "https://raw.githubusercontent.com/bunkerity/bunkerweb/master/docs/assets/img/logo.svg", "BunkerWeb GitHub"),
]

def valid_file(path: Path):
    data = path.read_bytes()
    if len(data) < 80:
        return False, f"too small ({len(data)}b)"
    head = data[:512].lstrip().lower()
    if path.suffix == '.svg':
        if b'<svg' not in head and b'<?xml' not in head and b'<html' not in head:
            return False, 'not svg/xml'
        if b'<html' in head:
            return False, 'html page'
    elif path.suffix == '.png':
        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            return False, 'not png'
    return True, f"ok {len(data)}b"

results = []
tried_names = set()
# try in order, first success per name wins
for name, url, note in ITEMS:
    dest = OUT / name
    if dest.exists():
        ok, msg = valid_file(dest)
        if ok:
            results.append((name, "EXISTS", msg, url, note))
            tried_names.add(name)
            continue
        dest.unlink(missing_ok=True)
    # if already succeeded earlier in this run for same name, skip
    prev = [r for r in results if r[0]==name and r[1] in ("DOWNLOADED","EXISTS")]
    if prev:
        continue
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

# report per name summary (best)
from collections import OrderedDict
summary = OrderedDict()
for name, status, msg, url, note in results:
    if status in ("DOWNLOADED","EXISTS"):
        summary[name] = (status,msg,url,note)
    elif name not in summary:
        summary.setdefault(name, (status,msg,url,note))
print("== SUMMARY ==")
for name,(status,msg,url,note) in summary.items():
    print("|".join([name,status,msg,url,note]))
print("== ALL ATTEMPTS ==")
for r in results:
    print("|".join(r))
