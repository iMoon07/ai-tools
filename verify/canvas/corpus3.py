import json, subprocess, time, urllib.parse, urllib.request, sys, base64, shutil, glob, os

ROOT = "http://127.0.0.1:8778"
PAGE = ROOT + "/imoon07.github.io/read.html?url="
PORT = 9414
PROF = "/tmp/alur-probes/prof-corpus3"
DOCS = sorted(glob.glob("/home/moon/Projects/Penjelajah-CyberSecurity/**/*.md", recursive=True))
DOCS = [d for d in DOCS if "```topology" in open(d, encoding="utf-8", errors="ignore").read()]
DOCS = [d for d in DOCS if "server-single-tier-stack-en" in d or "template-for-you-preview" in d]

shutil.rmtree(PROF, ignore_errors=True)
proc = subprocess.Popen(["chromium", "--headless=new", f"--remote-debugging-port={PORT}",
    f"--user-data-dir={PROF}", "--no-first-run", "--no-default-browser-check",
    "--disable-gpu", "--window-size=1400,1100", "--remote-allow-origins=*", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
import websocket

def http(p, method="GET"):
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(f"http://127.0.0.1:{PORT}{p}", method=method), timeout=10).read())

for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)

def newtab():
    t = http("/json/new?" + urllib.parse.quote("about:blank", safe=""), method="PUT")
    return websocket.create_connection(t["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)

def run(ws, cmds):
    n = [0]
    def send(m, **p):
        n[0] += 1
        ws.send(json.dumps({"id": n[0], "method": m, "params": p}))
        while True:
            r = json.loads(ws.recv())
            if r.get("id") == n[0]:
                if "error" in r: raise RuntimeError(r["error"])
                return r.get("result", {})
    return send

EXPR = r"""
(() => {
  const out = [];
  for (const root of document.querySelectorAll('.topology')) {
    const boxes = [...root.querySelectorAll('.topo-node')].map(el => {
      const r = el.getBoundingClientRect();
      return {x:r.x,y:r.y,w:r.width,h:r.height,t:(el.textContent||'').trim().slice(0,20)};
    });
    let cross = 0, dangling = 0, total = 0;
    for (const p of root.querySelectorAll('path')) {
      const len = p.getTotalLength ? p.getTotalLength() : 0;
      if (!len) continue;
      total++;
      const m = p.getScreenCTM();
      if (!m) continue;
      const toS = (pt) => ({x: m.a*pt.x + m.c*pt.y + m.e, y: m.b*pt.x + m.d*pt.y + m.f});
      const hit = new Set();
      for (let i = 0; i <= 60; i++) {
        const q = toS(p.getPointAtLength(len*i/60));
        boxes.forEach((B, bi) => {
          if (q.x > B.x+2 && q.x < B.x+B.w-2 && q.y > B.y+2 && q.y < B.y+B.h-2) hit.add(bi);
        });
      }
      if (hit.size) cross++;
      // endpoint must sit on a node border (within 3px)
      const near = (q) => boxes.some(B =>
        (q.x >= B.x-3 && q.x <= B.x+B.w+3 && q.y >= B.y-3 && q.y <= B.y+B.h+3));
      if (!near(toS(p.getPointAtLength(0))) || !near(toS(p.getPointAtLength(len)))) dangling++;
    }
    out.push({nodes: boxes.length, paths: total, cross: cross, dangling: dangling});
  }
  return JSON.stringify(out);
})()
"""

def measure(ws, send, url, label):
    send("Page.enable"); send("Runtime.enable")
    
    send("Emulation.setDeviceMetricsOverride", width=1400, height=1100, deviceScaleFactor=1, mobile=False)
    send("Page.navigate", url=url)
    time.sleep(5)
    send("Runtime.evaluate", expression="document.querySelectorAll('.topo-node').forEach(e=>e.scrollIntoView())")
    time.sleep(1)
    r = send("Runtime.evaluate", expression=EXPR, returnByValue=True)
    try:
        blocks = json.loads(r["result"]["value"])
    except Exception:
        blocks = []
    print(f"-- {label}{' (nobus)' if os.environ.get('NO_BUS') else ''}")
    for i, b in enumerate(blocks):
        flag = "  <<<" if (b["cross"] or b["dangling"]) else ""
        print(f"   block {i}: nodes={b['nodes']} paths={b['paths']} cross={b['cross']} dangling={b['dangling']}{flag}")
    return blocks

ws = newtab(); send = run(ws, None)
tot_c = tot_d = 0
for d in DOCS:
    url = PAGE + urllib.parse.quote("http://127.0.0.1:8778/" + os.path.relpath(d, "/home/moon/Projects"), safe="")
    bl = measure(ws, send, url, os.path.basename(d))
    tot_c += sum(b["cross"] for b in bl); tot_d += sum(b["dangling"] for b in bl)
print(f"TOTAL cross={tot_c} dangling={tot_d}")
proc.terminate()