import json
import re
import subprocess
import sys

CHROME = "/usr/bin/chromium"
LANGS = ["en", "id", "ms", "tl"]
VPS = ["1280,900", "390,844"]


def run(lang, vp):
    out = subprocess.run(
        [CHROME, "--headless", "--no-sandbox", "--disable-gpu",
         f"--window-size={vp}", "--virtual-time-budget=5000",
         "--dump-dom", f"file:///home/moon/Projects/ai-tools/snapshots/pages/harness-{lang}.html"],
        capture_output=True, text=True, timeout=90,
    ).stdout
    m = re.search(r'<pre id="report">(.*?)</pre>', out, re.S)
    if not m:
        return None
    return json.loads(m.group(1))


def main():
    bad = 0
    for lang in LANGS:
        for vp in VPS:
            d = run(lang, vp)
            if d is None:
                print(f"[{lang} {vp}] NO REPORT")
                bad += 1
                continue
            overlaps = [len(b.get("overlaps", [])) for b in d["blocks"]]
            scales = [b.get("zoom") for b in d["blocks"]]
            sizes = [(b.get("canvas"), b.get("cols")) for b in d["blocks"]]
            ok = d["topo"] == 3 and d["mermaid"] == 0 and sum(overlaps) == 0
            if not ok:
                bad += 1
            print(f"[{lang} {vp}] {'OK ' if ok else 'BAD'} topo={d['topo']} mermaid={d['mermaid']} "
                  f"nodes={d.get('nodeCount')} overlaps={overlaps} scales={scales}")
            if not ok:
                print(f"        sizes={sizes}")
    print("ALL OK" if bad == 0 else f"{bad} FAILURES")


if __name__ == "__main__":
    main()