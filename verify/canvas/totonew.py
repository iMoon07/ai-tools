import json, subprocess, time, urllib.parse, urllib.request, shutil, pathlib, re, sys
PORT = 9671; PROF = "/tmp/alur-probes/prof-totonew"
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
ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=90, suppress_origin=True)
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

FILES = [
    "/home/moon/Projects/Penjelajah-CyberSecurity/blog-post-template/template-for-you-en.md",
    "/home/moon/Projects/Penjelajah-CyberSecurity/blog-post-template/template-for-you-preview.md",
    "/home/moon/Projects/Penjelajah-CyberSecurity/Experiments/foundations/server-architecture/server-single-tier-stack-en.md",
]
BLOCKS = []
for f in FILES:
    txt = pathlib.Path(f).read_text()
    for i, b in enumerate(re.findall(r'```topology[ \t]*\n([\s\S]*?)\n```', txt)):
        BLOCKS.append((pathlib.Path(f).name + f"#{i}", b))

pathlib.Path('/tmp/alur-probes/totonew_art.html').write_text(
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

SHAPE = """(()=>{
 const p=document.querySelector('#wrap .tp');
 if(!p) return {err:'no .tp'};
 const nodes=[...p.querySelectorAll('.tp-node')];
 const cols=[...p.querySelectorAll('.tp-col')];
 const edges=[...p.querySelectorAll('.tp-wires-g > *')].length;
 const imgs=[...p.querySelectorAll('.tp-icon')].map(s=>{
   const u=s.querySelector('use'); const im=s.querySelector('image');
   return im? 'img:'+(im.getAttribute('href')||'').slice(0,40) : (u? (u.getAttribute('href')||'') : 'none');});
 const empty=nodes.filter(nd=>!nd.querySelector('.tp-node-label')||!nd.querySelector('.tp-node-label').textContent.trim());
 return {title:(p.querySelector('.tp-title')||{}).textContent||'',
   nodes:nodes.length, cols:cols.length, edges,
   colW:cols.map(c=>Math.round(c.getBoundingClientRect().width)),
   boardW:Math.round(p.querySelector('.tp-board').getBoundingClientRect().width),
   boardH:Math.round(p.querySelector('.tp-board').getBoundingClientRect().height),
   emptyLabels:empty.length, icons:imgs.filter(x=>x!=='none').length,
   missingIcons:imgs.filter(x=>x==='none').length,
   badIcons:imgs.filter(x=>{const u=x.match(/^#(i-[a-z0-9:_-]+)$/);return u&&!document.getElementById(u[1]);}).slice(0,4),
   wires:(()=>{const w=p.querySelector('.tp-wires');return w?[w.getAttribute('viewBox'),Math.round(w.getBoundingClientRect().width)]:null})(),
   overflow: p.scrollWidth>p.clientWidth+1,
   err: p.textContent.indexOf('Diagram gagal')>-1?'render-fail':(p.textContent.indexOf('Diagram tidak valid')>-1?'parse-fail':'')};
})()"""

send("Emulation.setDeviceMetricsOverride", width=1600, height=1000, deviceScaleFactor=1, mobile=False)
send("Page.navigate", url="file:///tmp/alur-probes/totonew_art.html"); time.sleep(2.0)

for tag, src in BLOCKS:
    ev("(()=>{const w=document.getElementById('wrap');w.innerHTML='';"
       "const d=document.createElement('div');w.appendChild(d);"
       "d.setAttribute('data-spec', %s);"
       "window.Topo.renderText(d, d.getAttribute('data-spec'));return 1})()" % json.dumps(src))
    time.sleep(1.6)
    print(tag.ljust(30), json.dumps(ev(SHAPE)))

# viewport sempit: cek tidak ada overflow horizontal untuk semua blok
send("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
send("Page.navigate", url="file:///tmp/alur-probes/totonew_art.html"); time.sleep(1.8)
worst = []
for tag, src in BLOCKS:
    ev("(()=>{const w=document.getElementById('wrap');w.style.width='346px';w.innerHTML='';"
       "const d=document.createElement('div');w.appendChild(d);"
       "d.setAttribute('data-spec', %s);window.Topo.renderText(d, d.getAttribute('data-spec'));return 1})()"
       % json.dumps(src))
    time.sleep(1.0)
    r = ev("""(()=>{const p=document.querySelector('.tp'); if(!p) return {err:'none'};
     const nodes=[...p.querySelectorAll('.tp-node')];
     return {ov:p.scrollWidth>p.clientWidth+1,
       doc:document.documentElement.scrollWidth>document.documentElement.clientWidth+1,
       minNode:Math.min(...nodes.map(nd=>nd.getBoundingClientRect().width)),
       maxNode:Math.max(...nodes.map(nd=>nd.getBoundingClientRect().width)),
       rows:new Set(nodes.map(nd=>Math.round(nd.getBoundingClientRect().top))).size,
       cols:new Set(nodes.map(nd=>Math.round(nd.getBoundingClientRect().left))).size};})()""")
    worst.append((tag, r))
for tag, r in worst:
    flag = 'OVERFLOW' if r.get('ov') or r.get('doc') else 'ok'
    print(tag.ljust(30), flag, json.dumps(r))
print("exceptions:", exc if exc else "none")
try: proc.terminate()
except Exception: pass