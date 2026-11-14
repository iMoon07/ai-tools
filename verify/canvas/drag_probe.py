import json, subprocess, time, urllib.parse, urllib.request, shutil, sys

PORT = 9461
PROF = "/tmp/kilo/prof-drag"
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
    r = send("Runtime.evaluate", expression=e, returnByValue=True)
    res = r.get("result", {})
    if res.get("subtype") == "error":
        return "ERR " + str(res.get("description"))[:200]
    return res.get("value")

send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride", width=1400, height=1000, deviceScaleFactor=1, mobile=False)
send("Page.navigate", url="http://127.0.0.1:8123/draw.html")
time.sleep(4)
ev("document.querySelector('[data-scene-module=flow]').click()")
time.sleep(2)

def heads():
    return ev("""(()=>{const hs=[...document.querySelectorAll('.alur-edge-head')];
      return JSON.stringify({count:hs.length,
        hidden:hs.filter(h=>h.style.opacity==='0').length,
        sample:hs.slice(0,2).map(h=>h.getAttribute('d'))});})()""")

print("before drag:", heads())

# find a node's screen position and drag it 120px right
box = ev("""(()=>{const el=document.querySelector('.alur-canvas-node[data-node-id]');
  const r=el.getBoundingClientRect(); return JSON.stringify({id:el.getAttribute('data-node-id'),
  x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2)});})()""")
print("node:", box)
b = json.loads(box)

def mouse(kind, x, y, extra=None):
    p = {"type": "mouse" + kind, "x": x, "y": y, "button": "left", "clickCount": 1}
    if extra: p.update(extra)
    send("Input.dispatchMouseEvent", **p)

mouse("Pressed", b["x"], b["y"])
for step in range(1, 7):
    mouse("Moved", b["x"] + step * 20, b["y"] + step * 10)
    time.sleep(0.12)
    if step in (2, 4, 6):
        print(f"  mid-drag {step}:", heads())
mouse("Released", b["x"] + 120, b["y"] + 60)
time.sleep(1.5)
print("after drop:", heads())

# second drag to check it stays fixed
mouse("Pressed", b["x"] + 120, b["y"] + 60)
for step in range(1, 5):
    mouse("Moved", b["x"] + 120 - step * 30, b["y"] + 60 - step * 15)
    time.sleep(0.12)
mouse("Released", b["x"], b["y"])
time.sleep(1.5)
print("after 2nd drop:", heads())

print("arrowheads visible:", ev("""(()=>{const hs=[...document.querySelectorAll('.alur-edge-head')];
  const v=hs.filter(h=>{const c=getComputedStyle(h);const r=h.getBoundingClientRect();
    return c.opacity!=='0' && c.display!=='none' && r.width>0;});
  return v.length+'/'+hs.length;})()"""))

ws.close(); proc.terminate()