import json, subprocess, time, urllib.parse, urllib.request, shutil, os

PORT = 9441
PROF = "/tmp/alur-probes/prof-round"
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
            if r.get("method") == "Runtime.exceptionThrown":
                print("  [exception]", r["params"]["exceptionDetails"].get("text"))
            if r.get("error"): raise RuntimeError(r["error"])
            return r.get("result", {})

def ev(e):
    r = send("Runtime.evaluate", expression=e, returnByValue=True, awaitPromise=True)
    res = r.get("result", {})
    return res.get("value")

send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride", width=1400, height=1000, deviceScaleFactor=1, mobile=False)
send("Page.navigate", url="http://127.0.0.1:8123/draw.html")
time.sleep(4)

print("1. insert topology block")
ev("document.querySelector('[data-scene-module=topology]').click()")
time.sleep(2)
print("   block:", ev("(()=>{const e=document.querySelector('.alur-module-embed[data-module=topology]');return e?e.querySelectorAll('.topo-node').length:'none'})()"),
      "nodes")

print("2. export spec from the editor")
spec = ev("document.getElementById('spec').value")
print("   spec chars:", len(spec) if spec else 0)

print("3. edit inside the block (add a node + turn grid off) and re-export")
edited = ev("""(()=>{
  const s = JSON.parse(document.getElementById('spec').value);
  const id = Object.keys(s.nodes).find(k=>s.nodes[k].shape==='module' && s.nodes[k].module==='topology');
  const ms = s.nodes[id].moduleSpec;
  ms.grid = false;
  ms.title = 'Edited in draw';
  ms.nodes['X'] = ['Cache','ready to serve','package','store'];
  ms.columns = [['C'],['P'],['K'],['G'],['X']];
  ms.edges = ms.edges.concat([['G','X']]);
  document.getElementById('spec').value = JSON.stringify(s, null, 2);
  document.getElementById('apply').click();
  return {id: id, cols: ms.columns.length, nodes: Object.keys(ms.nodes).length};
})()""")
print("   ", edited)
time.sleep(2)

print("4. rendered after edit:", ev("(()=>{const e=document.querySelector('.alur-module-embed[data-module=topology]');const h=e&&(e.closest('.alur-topology')||e.parentElement);return e?e.querySelectorAll('.topo-node').length+' nodes, grid='+(h?h.className:'?'):'none'})()"))

spec2 = ev("document.getElementById('spec').value")
os.makedirs("/tmp/alur-probes/rt", exist_ok=True)
md = "# round trip\n\n```draw\n" + spec2 + "\n```\n"
open("/tmp/alur-probes/rt/rt.md", "w").write(md)

# serve it from the docs dir so read.html can fetch it same-origin
dst = "/home/moon/Projects/Penjelajah-CyberSecurity/.tmp-rt.md"
open(dst, "w").write(md)
print("5. write md:", len(md), "bytes")

t2 = http("/json/new?" + urllib.parse.quote("about:blank", safe=""), method="PUT")
ws2 = websocket.create_connection(t2["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
n2 = [0]
def send2(m, **p):
    n2[0] += 1
    ws2.send(json.dumps({"id": n2[0], "method": m, "params": p}))
    while True:
        r = json.loads(ws2.recv())
        if r.get("id") == n2[0]:
            if r.get("error"): raise RuntimeError(r["error"])
            return r.get("result", {})
def ev2(e):
    return send2("Runtime.evaluate", expression=e, returnByValue=True).get("result", {}).get("value")

send2("Runtime.enable"); send2("Page.enable")
send2("Emulation.setDeviceMetricsOverride", width=1200, height=1000, deviceScaleFactor=1, mobile=False)
send2("Page.navigate", url="http://127.0.0.1:8123/read.html?url=" + urllib.parse.quote("http://127.0.0.1:8123/docs/.tmp-rt.md", safe=""))
time.sleep(7)
print("6. read.html render of the exported block:")
print("  ", ev2("""(()=>{const b=document.querySelector('.alur');
  if(!b) return 'no block';
  const h=b.querySelector('.alur-topology');
  return JSON.stringify({nodes:b.querySelectorAll('.topo-node').length,
    gridClass:h?h.className:null, title:b.getAttribute('data-title'),
    w:Math.round(b.getBoundingClientRect().width)});})()"""))

os.remove(dst)
proc.terminate()