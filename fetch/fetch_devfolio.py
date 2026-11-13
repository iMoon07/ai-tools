#!/usr/bin/env python3
import urllib.request
from pathlib import Path

OUT = Path("/home/moon/Projects/logo")
OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://raw.githubusercontent.com/drtinkerer/devfolio/main/public/floating-icons"

ALL = [
    "Apple.svg","Cloudflare.svg","GitLab.svg","Grafana.svg","Helm.svg","Jenkins.svg","Prometheus.svg","Slack.svg","Vim.svg",
    "airflow.svg","ansible.svg","apache.svg","arch-linux.svg","argocd.svg","aws.svg","bash.svg","docker.svg","elasticsearch.svg",
    "gcp.svg","git.svg","github-actions.svg","go.svg","hadoop.svg","javascript.svg","kafka.svg","kubernetes.svg","linux.svg","ml.svg",
    "nginx.svg","openai.svg","opentelemetry.svg","python.svg","raspberry-pi.svg","redis.svg","spark.svg","streamlit.svg","swagger.svg",
    "terraform.svg","trafik.svg","ubuntu.svg","vault.svg","video-game.svg","vscode.svg","windows.svg",
]

# stack & cybersec/infra relevant
RELEVANT = {
    "Cloudflare.svg","GitLab.svg","Grafana.svg","Helm.svg","Jenkins.svg","Prometheus.svg",
    "airflow.svg","ansible.svg","apache.svg","arch-linux.svg","argocd.svg","aws.svg","bash.svg",
    "docker.svg","elasticsearch.svg","gcp.svg","git.svg","github-actions.svg","go.svg","hadoop.svg",
    "javascript.svg","kafka.svg","kubernetes.svg","linux.svg","nginx.svg","opentelemetry.svg","python.svg",
    "raspberry-pi.svg","redis.svg","spark.svg","swagger.svg","terraform.svg","trafik.svg","ubuntu.svg",
    "vault.svg","windows.svg",
}
SKIPPED = [n for n in ALL if n not in RELEVANT]

def norm_name(name: str) -> str:
    # keep lowercase, preserve meaningful chars
    n = name.lower()
    return n

def valid_svg(data: bytes) -> bool:
    if len(data) < 50:
        return False
    head = data[:512].lstrip().lower()
    return b"<svg" in head or b"<?xml" in head

print("== RELEVANT (stack & cybersec/infra) ==")
for n in sorted(RELEVANT):
    print(n)
print("\n== SKIPPED (not stack/cybersec focus) ==")
for n in sorted(SKIPPED):
    print(n)

results = []
for name in sorted(RELEVANT):
    out_name = norm_name(name)
    # avoid duplicating content if same logical tool already present under different name
    # (keep devfolio version only if missing)
    dest = OUT / out_name
    if dest.exists():
        results.append((name, out_name, "EXISTS", "already present"))
        continue
    url = f"{BASE}/{name}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "logo-fetcher/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        if not valid_svg(data):
            results.append((name, out_name, "FAIL", "invalid svg"))
            continue
        dest.write_bytes(data)
        results.append((name, out_name, "DOWNLOADED", f"ok {len(data)}b"))
    except Exception as e:
        results.append((name, out_name, "FAIL", str(e)))

print("\n== DOWNLOAD RESULTS ==")
for r in results:
    print("|".join(r))
ok = sum(1 for r in results if r[2] in ("DOWNLOADED","EXISTS"))
new = sum(1 for r in results if r[2] == "DOWNLOADED")
print(f"\nTOTAL_OK={ok} NEW={new}")
