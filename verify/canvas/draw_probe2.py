import json, subprocess, time, urllib.parse, urllib.request, shutil

PORT = 9432
PROF = "/tmp/alur-probes/prof-draw2"
BASE = "http://127.0.0.1:8123/draw.html"
shutil.rmtree(PROF, ignore_errors=True)
proc = subprocess.Popen(["chromium", "--headless=new", f"--remote-debugging-port={PORT}",
    f"--user-data-dir={PROF}", "--no-first-run", "--no-default-browser-check",
    "--disable-gpu", "--window-size=1400,1000", "--remote-allow-origins=*", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
import websocket

def http(p, method="GET"):
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(f"http://127.0.0.1:{PORT}{p}", method=method), timeout=10).read())

for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)

t = http("/json/new?" + urllib.parse.quote("about:blank", safe=""), method="PUT")
ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
n = [0]
def send(m, **p):
    n[0] += 1
    ws.send(json.dumps({"id": n[0], "method": m, "params": p}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == n[0]:
            if r.get("error"): raise RuntimeError(r["error"])
            return r.get("result", {})

def ev(e):
    r = send("Runtime.evaluate", expression=e, returnByValue=True)
    res = r.get("result", {})
    if res.get("subtype") == "error":
        return "ERR " + str(res.get("description"))
    return res.get("value")

def run(width, height, label):
    send("Runtime.enable"); send("Page.enable")
    send("Emulation.setDeviceMetricsOverride", width=width, height=height, deviceScaleFactor=1, mobile=width < 700)
    send("Page.navigate", url=BASE)
    time.sleep(4)
    ev("document.querySelector('[data-scene-module=topology]').click()")
    time.sleep(2)
    print(f"== {label} ({width}x{height}) ==")
    print(" ", ev("""(()=>{
      const emb = document.querySelector('.alur-module-embed[data-module=topology]');
      if (!emb) return 'no embed';
      const host = emb.querySelector('.alur-host');
      const holder = emb.querySelector('.alur-topology');
      const root = emb.querySelector('.topology');
      const stage = emb.querySelector('.topo-stage');
      const canvas = emb.querySelector('.topo-canvas');
      const cols = emb.querySelector('.topo-columns');
      const r = e => e ? Math.round(e.getBoundingClientRect().width) : null;
      return JSON.stringify({
        emb: r(emb), host: r(host), holder: r(holder), root: r(root),
        stage: r(stage), canvas: r(canvas), cols: r(cols),
        holderStyle: holder ? holder.getAttribute('style') : null,
        holderClass: holder ? holder.className : null,
        rootClass: root ? root.className : null,
        bgImage: holder ? getComputedStyle(holder).backgroundImage.slice(0,50) : null,
        bgSize: holder ? getComputedStyle(holder).backgroundSize.slice(0,50) : null,
        embScroll: [emb.scrollWidth, emb.clientWidth]
      });
    })()"""))

run(1400, 1000, "desktop")
run(390, 844, "mobile")
ws.close()
proc.terminate()