import json, subprocess, time, urllib.parse, urllib.request, shutil, pathlib, re
PORT = 9691; PROF = "/tmp/alur-probes/prof-topodata"
shutil.rmtree(PROF, ignore_errors=True)
proc = subprocess.Popen(["chromium", "--headless=new", f"--remote-debugging-port={PORT}",
    f"--user-data-dir={PROF}", "--no-first-run", "--no-default-browser-check", "--disable-gpu",
    "--window-size=1600,1000", "--remote-allow-origins=*", "--hide-scrollbars", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
import websocket

def http(p, method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}", method=method), timeout=10).read())

for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)

t = http("/json/new?" + urllib.parse.quote("about:blank", safe=""), method="PUT")
ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
n = [0]; exc = []

def send(m, **p):
    n[0] += 1; ws.send(json.dumps({"id": n[0], "method": m, "params": p}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == n[0]: return r.get("result", {})
        if r.get("method") == "Runtime.exceptionThrown":
            d = r["params"]["exceptionDetails"]
            exc.append(d.get("text", "") + " " + (d.get("exception") or {}).get("description", "")[:200])

def ev(e):
    r = send("Runtime.evaluate", expression=e, returnByValue=True, awaitPromise=True).get("result", {})
    return r.get("value") if r.get("subtype") != "error" else {"__err": r.get("description")}

send("Runtime.enable"); send("Page.enable")

txt = pathlib.Path('/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture/server-single-tier-stack-en.md').read_text()
blocks = re.findall(r'```topology[ \t]*\n([\s\S]*?)\n```', txt)

pathlib.Path('/tmp/alur-probes/topodata_art.html').write_text(
    "<!doctype html><html><head><meta charset='utf-8'>"
    "<link rel='stylesheet' href='http://127.0.0.1:8123/css/topo.css?v=1'>"
    "<style>body{margin:0;background:#0d1117;color:#c9d1d9;font:13px/1.55 system-ui}"
    "#wrap{width:670px;margin:0 auto;padding:24px}</style></head><body>"
    "<div id='wrap'></div>"
    "<script src='http://127.0.0.1:8123/js/topology-icons.js?v=6'></script>"
    "<script src='http://127.0.0.1:8123/js/logo-manifest.js'></script>"
    "<script src='http://127.0.0.1:8123/js/alur/logos.js?v=5'></script>"
    "<script src='http://127.0.0.1:8123/js/topo-lang.js?v=1'></script>"
    "<script src='http://127.0.0.1:8123/js/topo.js?v=1'></script></body></html>")

send("Emulation.setDeviceMetricsOverride", width=1600, height=1000, deviceScaleFactor=1, mobile=False)
send("Page.navigate", url="file:///tmp/alur-probes/topodata_art.html"); time.sleep(1.8)

# tiru markdown.js: escapeHtml(token.spec) -> atribut data-spec -> Topo.init()
esc = lambda s: (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                  .replace('"', '&quot;'))
html = ''.join('<div class="topology" data-spec="%s"></div>' % esc(b) for b in blocks)
ev("(()=>{document.getElementById('wrap').innerHTML=%s;return 1})()" % json.dumps(html))
time.sleep(0.4)
ev("window.Topo.init()")
time.sleep(2.0)

print(json.dumps(ev("""(()=>{
 const ds=[...document.querySelectorAll('.topology')];
 return {blocks:ds.length,
   rendered:ds.filter(d=>d.querySelector('.tp-board')).length,
   failText:ds.filter(d=>/Diagram (gagal|tidak)/.test(d.textContent)).length,
   titles:[...document.querySelectorAll('.tp-title')].map(e=>e.textContent),
   nodes:document.querySelectorAll('.tp-node').length,
   edges:document.querySelectorAll('.tp-wires-g > *').length,
   emptyLabels:[...document.querySelectorAll('.tp-node')].filter(nd=>{
     const l=nd.querySelector('.tp-node-label');return !l||!l.textContent.trim();}).length,
   arrowMarkers:(()=>{const p=document.querySelector('.tp-wires path[marker-end]');
     return p?p.getAttribute('marker-end'):null})()};
})()"""), indent=1))
print("exceptions:", exc if exc else "none")
proc.terminate()