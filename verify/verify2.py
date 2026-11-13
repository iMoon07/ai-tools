import json, re, subprocess
CHROME="/usr/bin/chromium"; LANGS=["en","id","ms","tl"]; VPS=["1280,900","390,844"]
def run(lang,vp):
    out=subprocess.run([CHROME,"--headless","--no-sandbox","--disable-gpu",f"--window-size={vp}",
        "--virtual-time-budget=6000","--dump-dom",f"file:///home/moon/Projects/ai-tools/snapshots/pages/harness-{lang}.html"],
        capture_output=True,text=True,timeout=120).stdout
    m=re.search(r'<pre id="report">(.*?)</pre>',out,re.S)
    return json.loads(m.group(1)) if m else None
bad=0
for lang in LANGS:
    for vp in VPS:
        d=run(lang,vp)
        if d is None: print(lang,vp,"NO REPORT"); bad+=1; continue
        tot=sum(len(b.get("overlaps",[])) for b in d["blocks"])
        sizes=[(b.get("canvas"),b.get("zoom"),b.get("narrow")) for b in d["blocks"]]
        if tot: bad+=1
        print(f"[{lang} {vp}] blocks={d['topo']} nodes={d.get('nodeCount')} overlaps={tot} scales={[b.get('zoom') for b in d['blocks']]}")
        if tot:
            for b in d["blocks"]:
                if b.get("overlaps"): print("   block",b["i"],"overlaps",b["overlaps"][:6],"...",len(b["overlaps"]))
print("ALL OK" if bad==0 else f"{bad} FAILURES")
