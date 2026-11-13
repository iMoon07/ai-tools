#!/usr/bin/env python3
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

OUT = Path("/home/moon/Projects/logo")
OUT.mkdir(parents=True, exist_ok=True)

SI = "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons"

# (filename, url, note)
ITEMS = [
    # existing / core (will skip if present)
    ("kali-linux.svg", f"{SI}/kalilinux.svg", "Simple Icons"),
    ("metasploit.svg", f"{SI}/metasploit.svg", "Simple Icons"),
    ("burp-suite.svg", f"{SI}/burpsuite.svg", "Simple Icons"),
    ("wireshark.svg", f"{SI}/wireshark.svg", "Simple Icons"),
    ("docker.svg", f"{SI}/docker.svg", "Simple Icons"),
    ("kubernetes.svg", f"{SI}/kubernetes.svg", "Simple Icons"),
    ("linux.svg", f"{SI}/linux.svg", "Simple Icons"),
    ("splunk.svg", f"{SI}/splunk.svg", "Simple Icons"),
    ("owasp.svg", f"{SI}/owasp.svg", "Simple Icons"),
    ("grafana.svg", f"{SI}/grafana.svg", "Simple Icons"),
    ("prometheus.svg", f"{SI}/prometheus.svg", "Simple Icons"),
    ("elastic.svg", f"{SI}/elastic.svg", "Simple Icons"),
    ("parrot-security.svg", f"{SI}/parrotsecurity.svg", "Simple Icons"),
    ("ubuntu.svg", f"{SI}/ubuntu.svg", "Simple Icons"),
    ("debian.svg", f"{SI}/debian.svg", "Simple Icons"),
    ("tails.svg", f"{SI}/tails.svg", "Simple Icons"),
    ("git.svg", f"{SI}/git.svg", "Simple Icons"),
    ("github.svg", f"{SI}/github.svg", "Simple Icons"),
    ("gitlab.svg", f"{SI}/gitlab.svg", "Simple Icons"),
    ("python.svg", f"{SI}/python.svg", "Simple Icons"),
    ("go.svg", f"{SI}/go.svg", "Simple Icons"),
    ("rust.svg", f"{SI}/rust.svg", "Simple Icons"),
    ("gnu-bash.svg", f"{SI}/gnubash.svg", "Simple Icons"),
    ("openbsd.svg", f"{SI}/openbsd.svg", "Simple Icons"),
    ("freebsd.svg", f"{SI}/freebsd.svg", "Simple Icons"),
    ("snyk.svg", f"{SI}/snyk.svg", "Simple Icons"),
    ("bitwarden.svg", f"{SI}/bitwarden.svg", "Simple Icons"),
    ("keepassxc.svg", f"{SI}/keepassxc.svg", "Simple Icons"),
    ("openvpn.svg", f"{SI}/openvpn.svg", "Simple Icons"),
    ("wireguard.svg", f"{SI}/wireguard.svg", "Simple Icons"),
    ("virustotal.svg", f"{SI}/virustotal.svg", "Simple Icons"),
    ("tor-browser.svg", f"{SI}/torbrowser.svg", "Simple Icons"),
    ("nginx.svg", f"{SI}/nginx.svg", "Simple Icons"),
    ("postgresql.svg", f"{SI}/postgresql.svg", "Simple Icons"),
    ("android.svg", f"{SI}/android.svg", "Simple Icons"),
    ("gnome-terminal.svg", f"{SI}/gnometerminal.svg", "Simple Icons"),
    ("c.svg", f"{SI}/c.svg", "Simple Icons"),
    # new candidates
    ("sonarqube.svg", f"{SI}/sonarqube.svg", "Simple Icons"),
    ("hackthebox.svg", f"{SI}/hackthebox.svg", "Simple Icons"),
    ("tryhackme.svg", f"{SI}/tryhackme.svg", "Simple Icons"),
    ("letsencrypt.svg", f"{SI}/letsencrypt.svg", "Simple Icons"),
    ("cilium.svg", f"{SI}/cilium.svg", "Simple Icons"),
    ("suricata.svg", f"{SI}/suricata.svg", "Simple Icons"),
    ("snort.svg", f"{SI}/snort.svg", "Simple Icons"),
    ("openssl.svg", f"{SI}/openssl.svg", "Simple Icons"),
    ("gpg.svg", f"{SI}/gnuprivacyguard.svg", "Simple Icons"),
    ("malwarebytes.svg", f"{SI}/malwarebytes.svg", "Simple Icons"),
    ("cloudflare.svg", f"{SI}/cloudflare.svg", "Simple Icons"),
    ("pfsense.svg", f"{SI}/pfsense.svg", "Simple Icons"),
    ("opnsense.svg", f"{SI}/opnsense.svg", "Simple Icons"),
    ("redhat.svg", f"{SI}/redhat.svg", "Simple Icons"),
    ("fedora.svg", f"{SI}/fedora.svg", "Simple Icons"),
    ("arch-linux.svg", f"{SI}/archlinux.svg", "Simple Icons"),
    ("alpinelinux.svg", f"{SI}/alpinelinux.svg", "Simple Icons"),
    ("powershell.svg", f"{SI}/powershell.svg", "Simple Icons"),
    ("ansible.svg", f"{SI}/ansible.svg", "Simple Icons"),
    ("terraform.svg", f"{SI}/terraform.svg", "Simple Icons"),
    ("hashicorp.svg", f"{SI}/hashicorp.svg", "Simple Icons"),
    ("vault.svg", f"{SI}/vault.svg", "Simple Icons"),
    ("trivy.svg", f"{SI}/trivy.svg", "Simple Icons"),
    ("falco.svg", f"{SI}/falco.svg", "Simple Icons"),
    ("yara.svg", f"{SI}/yara.svg", "Simple Icons"),
    ("apache.svg", f"{SI}/apache.svg", "Simple Icons"),
    ("ngrok.svg", f"{SI}/ngrok.svg", "Simple Icons"),
    ("virtualbox.svg", f"{SI}/virtualbox.svg", "Simple Icons"),
    ("vmware.svg", f"{SI}/vmware.svg", "Simple Icons"),
    ("redis.svg", f"{SI}/redis.svg", "Simple Icons"),
    ("sqlite.svg", f"{SI}/sqlite.svg", "Simple Icons"),
    ("postgres.svg", f"{SI}/postgresql.svg", "Simple Icons"),
    # official/other (png fallback ok)
    ("trivy.png", "https://raw.githubusercontent.com/aquasecurity/trivy/main/docs/imgs/logo.png", "Aquasecurity GitHub"),
    ("mitre-attack.svg", "https://raw.githubusercontent.com/mitre-attack/attack-website/master/attack-theme/static/images/ATT&CK_red.svg", "MITRE ATT&CK site repo"),
    ("nuclei.svg", "https://raw.githubusercontent.com/projectdiscovery/nuclei/main/static/img/nuclei-logo.svg", "ProjectDiscovery GitHub"),
    ("sqlmap.png", "https://raw.githubusercontent.com/sqlmapproject/sqlmap/master/doc/images/sqlmap_logo.png", "sqlmap GitHub"),
    ("zap.png", "https://raw.githubusercontent.com/zaproxy/zaproxy/main/zap/src/main/dist/lang/images/zap128x128.png", "OWASP ZAP GitHub"),
    ("ghidra.png", "https://raw.githubusercontent.com/NationalSecurityAgency/ghidra/master/Ghidra/RuntimeScripts/Common/support/ghidra.ico", "Ghidra GitHub"),
]

def valid_file(path: Path) -> tuple[bool,str]:
    try:
        data = path.read_bytes()
    except Exception as e:
        return False, f"read error: {e}"
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

def download(url: str, dest: Path):
    req = urllib.request.Request(url, headers={"User-Agent":"logo-fetcher/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    dest.write_bytes(data)
    return len(data)

results = []
seen_names = set()
for name, url, note in ITEMS:
    if name in seen_names:
        results.append((name, "SKIP", "duplicate in list", url, note))
        continue
    seen_names.add(name)
    dest = OUT / name
    if dest.exists():
        ok, msg = valid_file(dest)
        if ok:
            results.append((name, "EXISTS", msg, url, note))
            continue
        else:
            dest.unlink(missing_ok=True)
    try:
        size = download(url, dest)
        ok, msg = valid_file(dest)
        if not ok:
            dest.unlink(missing_ok=True)
            results.append((name, "FAIL", f"downloaded but invalid: {msg}", url, note))
        else:
            results.append((name, "DOWNLOADED", msg, url, note))
    except Exception as e:
        results.append((name, "FAIL", str(e), url, note))

# summary
ok_count = sum(1 for r in results if r[1] in ("DOWNLOADED","EXISTS"))
print(f"TOTAL_OK={ok_count}")
for r in results:
    print("|".join([r[0], r[1], r[2], r[3], r[4]]))
