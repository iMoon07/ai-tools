import json, subprocess, time, urllib.parse, urllib.request, shutil, pathlib, re
PORT = 9723; PROF = "/tmp/alur-probes/prof-topoparity"
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

md = pathlib.Path('/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture/server-single-tier-stack-en.md').read_text()
blocks = re.findall(r'```topology[ \t]*\n([\s\S]*?)\n```', md)
esc = lambda s: (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'))

pathlib.Path('/tmp/alur-probes/topoparity_art.html').write_text(
    "<!doctype html><html><head><meta charset='utf-8'>"
    "<link rel='stylesheet' href='http://127.0.0.1:8123/css/topo.css?v=1'>"
    "<style>body{margin:0;background:#0d1117;color:#c9d1d9;font:13px/1.55 system-ui}"
    "#wrap{margin:0 auto;padding:20px;width:%dpx}</style></head><body>" % 670 + "<div id='wrap'></div>"
    "<script src='http://127.0.0.1:8123/js/topology-icons.js?v=6'></script>"
    "<script src='http://127.0.0.1:8123/js/logo-manifest.js'></script>"
    "<script src='http://127.0.0.1:8123/js/alur/logos.js?v=5'></script>"
    "<script src='http://127.0.0.1:8123/js/topo-lang.js?v=1'></script>"
    "<script src='http://127.0.0.1:8123/js/topo.js?v=1'></script></body></html>")

html = ''.join('<div class="topology" data-spec="%s"></div>' % esc(b) for b in blocks)

SHAPE = """(()=>{
 const p=document.querySelectorAll('.topology')[%d];
 const b=p.getBoundingClientRect();
 const nodes=[...p.querySelectorAll('.tp-node')].map(nd=>{
   const r=nd.getBoundingClientRect();
   return [nd.dataset.node||'', +((r.left-b.left)/b.width).toFixed(3),
           +((r.top-b.top)/b.width).toFixed(3), +(r.width/b.width).toFixed(3)];});
 const cols=[...p.querySelectorAll('.tp-col')].map(c=>{
   const r=c.getBoundingClientRect();
   return [+((r.left-b.left)/b.width).toFixed(3), +(r.width/b.width).toFixed(3)];});
 return {w:Math.round(b.width), nodeAbs:[...p.querySelectorAll('.tp-node')].slice(0,4).map(nd=>Math.round(nd.getBoundingClientRect().width)), cols:cols.length, nodes:nodes.length,
   edges:p.querySelectorAll('.tp-wires-g > *').length,
   colBoxes:cols, nodeBoxes:nodes};})()"""

for idx in (0, 2, 3):
    send("Page.navigate", url="file:///tmp/alur-probes/topoparity_art.html"); time.sleep(1.4)
    send("Emulation.setDeviceMetricsOverride", width=1600, height=1000, deviceScaleFactor=1, mobile=False)
    ev("(()=>{document.getElementById('wrap').innerHTML=%s;window.Topo.init();return 1})()" % json.dumps(html))
    time.sleep(1.8)
    desk = ev(SHAPE % idx)

    send("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    ev("(()=>{document.getElementById('wrap').style.width='346px';window.Topo.init();return 1})()")
    time.sleep(1.8)
    mob = ev(SHAPE % idx)

    print('block', idx, '| desktop w', desk['w'], 'nodeW', desk['nodeAbs'], 'cols', desk['cols'],
          '| mobile w', mob['w'], 'nodeW', mob['nodeAbs'], 'cols', mob['cols'])
    print('   colBoxes equal :', desk['colBoxes'] == mob['colBoxes'])
    print('   node order same:', [x[0] for x in desk['nodeBoxes']] == [x[0] for x in mob['nodeBoxes']])
    if desk['colBoxes'] != mob['colBoxes']:
        print('   desk', desk['colBoxes'][:4])
        print('   mob ', mob['colBoxes'][:4])
    if [x[0] for x in desk['nodeBoxes']] != [x[0] for x in mob['nodeBoxes']]:
        print('   desk nodes', [x[0] for x in desk['nodeBoxes']][:8])
        print('   mob  nodes', [x[0] for x in mob['nodeBoxes']][:8])

print('exceptions:', exc if exc else 'none')
proc.terminate()