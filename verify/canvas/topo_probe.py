import json, subprocess, time, urllib.parse, urllib.request, sys, os, base64, shutil

MD = "http://127.0.0.1:8778/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture/server-single-tier-stack-en.md"
PAGE = "http://127.0.0.1:8778/imoon07.github.io/read.html?url=" + urllib.parse.quote(MD, safe="")
PORT = 9411
PROF = "/tmp/kilo/prof-topo"

shutil.rmtree(PROF, ignore_errors=True)
proc = subprocess.Popen(
    ["chromium", "--headless=new", f"--remote-debugging-port={PORT}",
     f"--user-data-dir={PROF}", "--no-first-run", "--no-default-browser-check",
     "--disable-gpu", "--window-size=1280,1000", "--remote-allow-origins=*",
     "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

import websocket

def http(p, method="GET"):
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(f"http://127.0.0.1:{PORT}{p}", method=method), timeout=10).read())

for _ in range(80):
    try:
        http("/json/version"); break
    except Exception:
        time.sleep(0.3)

def newtab(url):
    t = http("/json/new?" + urllib.parse.quote(url, safe=""), method="PUT")
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
    n = [0]
    def send(m, **p):
        n[0] += 1
        ws.send(json.dumps({"id": n[0], "method": m, "params": p}))
        while True:
            r = json.loads(ws.recv())
            if r.get("id") == n[0]:
                if "error" in r:
                    raise RuntimeError(r["error"])
                return r.get("result", {})
    return ws, send

def measure(width, height, label):
    ws, send = newtab("about:blank")
    send("Page.enable")
    send("Runtime.enable")
    send("Emulation.setDeviceMetricsOverride", width=width, height=height,
         deviceScaleFactor=1, mobile=width < 700)
    send("Page.navigate", url=PAGE)
    time.sleep(6)
    send("Runtime.evaluate", expression=(
        "document.querySelectorAll('.topo-node').forEach(e=>e.scrollIntoView())"))
    time.sleep(1)
    expr = r"""
    (() => {
      const roots = [...document.querySelectorAll('.topology')];
      const out = {found: roots.length, blocks: []};
      for (const root of roots) {
        const svg = root.querySelector('svg');
        const nodes = [...root.querySelectorAll('.topo-node, .topo-node *')];
        const boxes = [...root.querySelectorAll('.topo-node')].map(el => {
          const r = el.getBoundingClientRect();
          return {x: r.x, y: r.y, w: r.width, h: r.height,
                  txt: (el.textContent || '').trim().slice(0, 28)};
        });
        const hits = [];
        for (const p of root.querySelectorAll('path')) {
          const len = p.getTotalLength ? p.getTotalLength() : 0;
          if (!len) continue;
          const cls = p.getAttribute('class') || '';
          const bad = new Set();
          for (let i = 0; i <= 80; i++) {
            const raw = p.getPointAtLength(len * i / 80);
            const m = p.getScreenCTM();
            const pt = m ? {x: m.a*raw.x + m.c*raw.y + m.e, y: m.b*raw.x + m.d*raw.y + m.f} : raw;
            for (let b = 0; b < boxes.length; b++) {
              const B = boxes[b];
              if (pt.x > B.x + 2 && pt.x < B.x + B.w - 2 &&
                  pt.y > B.y + 2 && pt.y < B.y + B.h - 2) { bad.add(b); }
            }
          }
          if (bad.size) hits.push({cls: cls, d: (p.getAttribute('d') || '').slice(0, 110),
                                   nodes: [...bad].map(i => boxes[i].txt)});
        }
        out.blocks.push({hits: hits, boxes: boxes.length});
      }
      return JSON.stringify(out);
    })()
    """
    r = send("Runtime.evaluate", expression=expr, returnByValue=True)
    data = json.loads(r["result"]["value"])
    print(f"== {label} ({width}x{height}) ==")
    for i, b in enumerate(data["blocks"]):
        print(f" block {i}: nodes={b['boxes']} crossings={len(b['hits'])}")
        for h in b["hits"][:14]:
            print("   -", h["cls"], "| hits", h["nodes"], "|", h["d"])
    shot = send("Page.captureScreenshot", format="png", captureBeyondViewport=False)
    open(f"/tmp/kilo/topo_{label}.png", "wb").write(base64.b64decode(shot["data"]))
    ws.close()

measure(1280, 1000, "desktop")
measure(420, 900, "mobile")
proc.terminate()