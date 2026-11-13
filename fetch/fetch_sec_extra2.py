#!/usr/bin/env python3
import urllib.request
from pathlib import Path

OUT = Path("/home/moon/Projects/logo")
OUT.mkdir(parents=True, exist_ok=True)

ITEMS = [
    # Wazuh
    ("wazuh.svg", "https://raw.githubusercontent.com/wazuh/wazuh-dashboard/main/src/core/server/core_app/assets/logos/wazuh_on_light.svg", "Wazuh dashboard GitHub"),
    ("wazuh.svg", "https://raw.githubusercontent.com/wazuh/wazuh-dashboard/master/src/core/server/core_app/assets/logos/wazuh_on_light.svg", "Wazuh dashboard GitHub (master)"),
    ("wazuh.svg", "https://wazuh.com/brand-assets/Wazuh-Logo.svg", "Wazuh brand assets"),
    ("wazuh.svg", "https://upload.wikimedia.org/wikipedia/commons/6/6c/Wazuh-2022-Logo.svg", "Wikimedia Commons"),
    # Suricata
    ("suricata.png", "https://suricata.io/wp-content/uploads/2023/09/Logo-Suricata-vert-R.jpg", "suricata.io branding"),
    ("suricata.png", "https://suricata.io/wp-content/uploads/2021/01/Logo-Final-Suricata-horiz-R.png", "suricata.io branding"),
    ("suricata.svg", "https://raw.githubusercontent.com/OISF/suricata-ids.org/master/static/images/suricata-logo.svg", "Suricata ids.org repo"),
    ("suricata.svg", "https://raw.githubusercontent.com/OISF/suricata.io/master/static/images/suricata.svg", "Suricata.io repo"),
    # Zeek
    ("zeek.svg", "https://raw.githubusercontent.com/zeek/zeek-website/master/static/img/zeek-logo-blue.svg", "Zeek website repo"),
    ("zeek.png", "https://zeek.org/wp-content/uploads/2020/04/zeek-logo-blue.png", "zeek.org"),
    ("zeek.svg", "https://upload.wikimedia.org/wikipedia/commons/d/d8/Zeek_logo.svg", "Wikimedia Commons"),
    # ModSecurity / CRS / Coraza WAF
    ("modsecurity.svg", "https://raw.githubusercontent.com/owasp-modsecurity/ModSecurity/v3/master/others/modsecurity_logo.svg", "ModSecurity GitHub"),
    ("modsecurity.svg", "https://raw.githubusercontent.com/SpiderLabs/ModSecurity/v3/master/others/modsecurity_logo.svg", "ModSecurity GitHub (SpiderLabs)"),
    ("coraza.svg", "https://raw.githubusercontent.com/corazawaf/coraza.io/main/docs/assets/images/coraza.svg", "Coraza.io repo"),
    ("coraza.svg", "https://raw.githubusercontent.com/corazawaf/coraza.io/main/static/img/coraza.svg", "Coraza.io repo"),
    ("coraza.svg", "https://coraza.io/assets/images/coraza.svg", "coraza.io"),
    ("coraza.png", "https://raw.githubusercontent.com/corazawaf/coraza/main/docs/logo.png", "Coraza GitHub"),
    ("owasp-crs.svg", "https://raw.githubusercontent.com/coreruleset/coreruleset/master/docs/images/crs-logo.svg", "OWASP CRS GitHub"),
    ("owasp-crs.svg", "https://coreruleset.org/images/crs-logo.svg", "coreruleset.org"),
    # C2
    ("sliver.png", "https://raw.githubusercontent.com/BishopFox/sliver/master/server/assets/sliver-logo.png", "Sliver GitHub"),
    ("sliver.png", "https://raw.githubusercontent.com/BishopFox/sliver/master/gui/public/sliver-logo.png", "Sliver GitHub"),
    ("sliver.svg", "https://sliver.sh/images/sliver-logo.svg", "sliver.sh"),
    ("mythic.png", "https://raw.githubusercontent.com/its-a-feature/Mythic/master/MythicReactUI/src/assets/mythic_logo.png", "Mythic GitHub"),
    ("mythic.png", "https://raw.githubusercontent.com/its-a-feature/Mythic/master/mythic-docker/src/webapp/src/assets/mythic.svg", "Mythic GitHub"),
    ("empire.png", "https://raw.githubusercontent.com/BC-SECURITY/Empire/main/empire/server/common/empire.png", "Empire GitHub (retry)"),
    ("empire.png", "https://raw.githubusercontent.com/BC-SECURITY/Empire/main/docs/images/empire.png", "Empire GitHub"),
    ("covenant.png", "https://raw.githubusercontent.com/cobbr/Covenant/master/Covenant/wwwroot/images/covenant.png", "Covenant GitHub"),
    # other IDS/WAF
    ("ossec.svg", "https://www.ossec.net/wp-content/uploads/2019/01/ossec_logo.svg", "ossec.net"),
    ("crowdsec.svg", "https://raw.githubusercontent.com/crowdsecurity/crowdsec-docs/main/crowdsec-docs/static/img/crowdsec_logo.svg", "CrowdSec docs"),
    ("crowdsec.svg", "https://cdn.crowdsec.net/logo/crowdsec-logo.svg", "CrowdSec CDN"),
    ("fail2ban.svg", "https://upload.wikimedia.org/wikipedia/commons/4/4b/Fail2ban_logo.svg", "Wikimedia Commons"),
    ("openwrt.svg", "https://raw.githubusercontent.com/openwrt/branding/master/logo/openwrt_logo_blue_and_dark_blue.svg", "OpenWrt branding"),
]

def valid_file(path: Path):
    data = path.read_bytes()
    if len(data) < 80:
        return False, f"too small ({len(data)}b)"
    head = data[:512].lstrip().lower()
    if path.suffix == '.svg':
        if b'<svg' not in head and b'<?xml' not in head:
            return False, 'not svg/xml'
        if b'<html' in head or b'<!doctype html' in head:
            return False, 'html page'
    elif path.suffix == '.png':
        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            return False, 'not png'
    elif path.suffix in ('.jpg', '.jpeg'):
        if not data.startswith(b'\xff\xd8'):
            return False, 'not jpeg'
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
