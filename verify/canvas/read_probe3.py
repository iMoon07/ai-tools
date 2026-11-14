import json, subprocess, time, urllib.parse, urllib.request, shutil

PORT = 9434
PROF = "/tmp/kilo/prof-read3"
MD = "http://127.0.0.1:8123/docs/.tmp-topology-test.md"
PAGE = "http://127.0.0.1:8123/read.html?url=" + urllib.parse.quote(MD, safe="")
shutil.rmtree(PROF, ignore_errors=True)
proc = subprocess.Popen(["chromium", "--headless=new", f"--remote-debugging-port={PORT}",
    f"--user-data-dir={PROF}", "--no-first-run", "--no-default-browser-check",
    "--disable-gpu", "--window-size=1200,1000", "--remote-allow-origins=*", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
import websocket

def http(p, method="GET"):
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(f"http://127.0.0.1:{PORT}{p}", method=method), timeout=10).read())

for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)

def run(width, height, label):
    t = http("/json/new?" + urllib.parse.quote("about:blank", safe=""), method="PUT")
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
    n = [0]
    def send(m, **p):
        n[0] += 1
        ws.send(json.dumps({"id": n[0], "method": m, "params": p}))
        while True:
            r = json.loads(ws.recv())
            if r.get("id") == n[0]:
                if r.get("method") == "Runtime.exceptionThrown":
                    print("   [exception]", r["params"]["exceptionDetails"].get("text"))
                return r.get("result", {})
    send("Runtime.enable"); send("Page.enable")
    send("Emulation.setDeviceMetricsOverride", width=width, height=height, deviceScaleFactor=1, mobile=width < 700)
    send("Page.navigate", url=PAGE)
    time.sleep(7)
    print(f"== {label} ({width}x{height}) ==")
    out = send("Runtime.evaluate", returnByValue=True, expression="""(()=>{
      const blocks = [...document.querySelectorAll('.alur')];
      const info = blocks.map((b, i) => {
        const spec = b.getAttribute('data-spec') || '';
        const mod = (spec.match(/"module"\\s*:\\s*"([a-z-]+)"/) || [])[1] || '?';
        const holder = b.querySelector('.alur-topology');
        const topo = b.querySelector('.topo-canvas');
        const heads = b.querySelectorAll('.alur-edge-head');
        return {
          i, mod,
          nodes: b.querySelectorAll('.topo-node').length,
          topoCanvas: !!topo,
          grid: holder ? holder.className : null,
          gridBg: holder ? getComputedStyle(holder).backgroundImage.slice(0, 24) : null,
          heads: heads.length,
          headSample: heads.length ? heads[0].getAttribute('d') : null,
          w: Math.round(b.getBoundingClientRect().width),
          overflow: b.scrollWidth > b.clientWidth + 2
        };
      });
      const native = [...document.querySelectorAll('.topology')].filter(t=>!t.closest('.alur'));
      return JSON.stringify({count: blocks.length, blocks: info,
        nativeTopo: native.length,
        nativeNodes: native.map(t=>t.querySelectorAll('.topo-node').length)});
    })()""")["result"]["value"]
    print(" ", out)
    ws.close()

run(1200, 1000, "desktop")
run(390, 844, "mobile")
proc.terminate()