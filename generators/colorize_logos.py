#!/usr/bin/env python3
import urllib.request
from pathlib import Path

OUT = Path("/home/moon/Projects/logo")

# filename -> simpleicons slug for CDN (https://cdn.simpleicons.org/{slug})
SLUG_MAP = {
    "alpinelinux.svg": "alpinelinux",
    "android.svg": "android",
    "ansible.svg": "ansible",
    "apache.svg": "apache",
    "arch-linux.svg": "archlinux",
    "bitwarden.svg": "bitwarden",
    "burp-suite.svg": "burpsuite",
    "c.svg": "c",
    "cilium.svg": "cilium",
    "cloudflare.svg": "cloudflare",
    "debian.svg": "debian",
    "docker.svg": "docker",
    "elastic.svg": "elastic",
    "falco.svg": "falco",
    "fedora.svg": "fedora",
    "freebsd.svg": "freebsd",
    "git.svg": "git",
    "github.svg": "github",
    "gitlab.svg": "gitlab",
    "gnu-bash.svg": "gnubash",
    "gnome-terminal.svg": "gnometerminal",
    "go.svg": "go",
    "gpg.svg": "gnuprivacyguard",
    "grafana.svg": "grafana",
    "hackthebox.svg": "hackthebox",
    "hashicorp.svg": "hashicorp",
    "kali-linux.svg": "kalilinux",
    "keepassxc.svg": "keepassxc",
    "kubernetes.svg": "kubernetes",
    "letsencrypt.svg": "letsencrypt",
    "linux.svg": "linux",
    "malwarebytes.svg": "malwarebytes",
    "metasploit.svg": "metasploit",
    "nginx.svg": "nginx",
    "ngrok.svg": "ngrok",
    "openbsd.svg": "openbsd",
    "openssl.svg": "openssl",
    "openvpn.svg": "openvpn",
    "opnsense.svg": "opnsense",
    "owasp.svg": "owasp",
    "parrot-security.svg": "parrotsecurity",
    "pfsense.svg": "pfsense",
    "postgresql.svg": "postgresql",
    "prometheus.svg": "prometheus",
    "python.svg": "python",
    "redhat.svg": "redhat",
    "redis.svg": "redis",
    "rust.svg": "rust",
    "snort.svg": "snort",
    "snyk.svg": "snyk",
    "sonarqubeserver.svg": "sonarqubeserver",
    "splunk.svg": "splunk",
    "sqlite.svg": "sqlite",
    "tails.svg": "tails",
    "terraform.svg": "terraform",
    "tor-browser.svg": "torbrowser",
    "trivy.svg": "trivy",
    "tryhackme.svg": "tryhackme",
    "ubuntu.svg": "ubuntu",
    "vault.svg": "vault",
    "virtualbox.svg": "virtualbox",
    "virustotal.svg": "virustotal",
    "vmware.svg": "vmware",
    "wireguard.svg": "wireguard",
    "wireshark.svg": "wireshark",
}

SKIP = {"powershell.svg", "trivy.png", "SOURCES.md"}

def valid_svg(data: bytes) -> bool:
    if len(data) < 50:
        return False
    head = data[:512].lstrip().lower()
    return b"<svg" in head or b"<?xml" in head

results = []
for name, slug in sorted(SLUG_MAP.items()):
    dest = OUT / name
    if not dest.exists():
        results.append((name, "MISS", "file not found"))
        continue
    url = f"https://cdn.simpleicons.org/{slug}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "logo-colorizer/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        if not valid_svg(data):
            results.append((name, "FAIL", "invalid svg from cdn"))
            continue
        dest.write_bytes(data)
        results.append((name, "OK", f"{len(data)}b"))
    except Exception as e:
        results.append((name, "FAIL", str(e)))

ok = sum(1 for r in results if r[1] == "OK")
print(f"COLORED={ok}")
for r in results:
    print("|".join(r))
print("---SKIPPED---")
for s in sorted(SKIP):
    print(s)
