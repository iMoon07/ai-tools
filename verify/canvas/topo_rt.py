import json, subprocess, time, urllib.parse, urllib.request, shutil, os

PORT = 9481
PROF = "/tmp/kilo/prof-topo-rt"
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

def newtab():
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
                if r.get("method") == "Runtime.exceptionThrown":
                    print("  [exception]", r["params"]["exceptionDetails"].get("text"))
                return r.get("result", {})
    return ws, send

ws, send = newtab()
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride", width=1400, height=1000, deviceScaleFactor=1, mobile=False)
send("Page.navigate", url="http://127.0.0.1:8123/topology.html")
time.sleep(4)

def ev(e):
    return send("Runtime.evaluate", expression=e, returnByValue=True).get("result", {}).get("value")

# edit: rename a node, add a logo, add a facility chip, turn badges off
print("edit:", ev("""(()=>{
  const s = JSON.parse(document.getElementById('specBox').value);
  s.nodes.P[0] = 'Waiter (edited)';
  s.nodes.P[2] = 'stack:nginx';
  s.facilities = ['On one machine', ['server','Core'], ['lock','Transport']];
  s.legend = { flow: 'Request', back: 'Response' };
  s.badges = false;
  document.getElementById('specBox').value = JSON.stringify(s, null, 2);
  document.getElementById('applyBtn').click();
  return 'applied';
})()"""))
time.sleep(2)
print("after apply:", ev("""JSON.stringify({
  nodes: document.querySelectorAll('#preview .topo-node').length,
  facs: document.querySelectorAll('#preview .topo-facility').length,
  logoImg: document.querySelectorAll('#preview .topo-icon--file').length,
  labels: [...document.querySelectorAll('#preview .topo-node')].map(n=>n.textContent.slice(0,22))
})"""))

spec = ev("JSON.stringify(JSON.parse(document.getElementById('specBox').value))")
md = "# round trip\n\n```topology\n" + ev("document.getElementById('specBox').value") + "\n```\n"
dst = "/home/moon/Projects/Penjelajah-CyberSecurity/.tmp-topo-rt.md"
open(dst, "w").write(md)
print("md bytes:", len(md))

ws2, send2 = newtab()
send2("Runtime.enable"); send2("Page.enable")
send2("Emulation.setDeviceMetricsOverride", width=1200, height=1000, deviceScaleFactor=1, mobile=False)
send2("Page.navigate", url="http://127.0.0.1:8123/read.html?url=" + urllib.parse.quote("http://127.0.0.1:8123/docs/.tmp-topo-rt.md", safe=""))
time.sleep(7)

def ev2(e):
    return send2("Runtime.evaluate", expression=e, returnByValue=True).get("result", {}).get("value")

print("read.html:", ev2("""(()=>{const t=document.querySelector('.topology');
  if(!t) return 'no topology block';
  return JSON.stringify({
    nodes: t.querySelectorAll('.topo-node').length,
    paths: t.querySelectorAll('path').length,
    facs: t.querySelectorAll('.topo-facility').length,
    logoImg: t.querySelectorAll('.topo-icon--file').length,
    bg: getComputedStyle(t).backgroundColor,
    labels: [...t.querySelectorAll('.topo-node')].map(n=>n.textContent.slice(0,22))
  });})()"""))

os.remove(dst)
proc.terminate()