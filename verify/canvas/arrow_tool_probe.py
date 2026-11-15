import json, subprocess, time, urllib.parse, urllib.request, shutil

PORT = 9502
PROF = "/tmp/alur-probes/prof-line3"
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
            if r.get("method") == "Runtime.exceptionThrown":
                print("  [exception]", r["params"]["exceptionDetails"].get("text"))
            return r.get("result", {})

def ev(e):
    r = send("Runtime.evaluate", expression=e, returnByValue=True)
    res = r.get("result", {})
    if res.get("subtype") == "error": return "ERR " + str(res.get("description"))[:160]
    return res.get("value")

def mouse(kind, x, y):
    send("Input.dispatchMouseEvent", type="mouse" + kind, x=x, y=y, button="left", clickCount=1)

send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride", width=1400, height=1000, deviceScaleFactor=1, mobile=False)
send("Page.navigate", url="http://127.0.0.1:8123/draw.html")
time.sleep(4)
ev("document.querySelector('[data-scene-module=flow]').click()")
time.sleep(2)

def stat(tag):
    print(tag, ev("""JSON.stringify({
      edges: document.querySelectorAll('.alur-cable').length,
      heads: document.querySelectorAll('.alur-edge-head').length,
      hidden: [...document.querySelectorAll('.alur-edge-head')].filter(h=>h.style.opacity==='0').length,
      visible: [...document.querySelectorAll('.alur-edge-head')].filter(h=>{const c=getComputedStyle(h);const r=h.getBoundingClientRect();return c.opacity!=='0'&&r.width>0;}).length
    })"""))

stat("flow:")

# switch to the line tool via the command palette entry
ev("""(()=>{const b=[...document.querySelectorAll('button')].filter(x=>x.offsetParent&&/^arrow$/i.test(x.textContent.trim()));
  if(b[0]) { b[0].click(); return b.length; } return 0;})()""")
time.sleep(1)
print("tool:", ev("document.body.className || 'n/a'"))

# draw a line on empty canvas
mouse("Pressed", 900, 700)
for i in range(1, 6):
    mouse("Moved", 900 + i * 25, 700 - i * 12)
    time.sleep(0.06)
mouse("Released", 1025, 640)
time.sleep(1.5)
stat("after arrow:")

# move a node with the select tool and confirm heads follow
ev("""(()=>{const b=[...document.querySelectorAll('button')].filter(x=>x.offsetParent&&/^select$/i.test(x.textContent.trim()));
  if(b[0]) b[0].click(); return 1;})()""")
time.sleep(0.6)
box = ev("""(()=>{const el=document.querySelector('.alur-canvas-node[data-node-id]');
  if(!el) return null; const r=el.getBoundingClientRect();
  return JSON.stringify({id:el.getAttribute('data-node-id'),x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)});})()""")
if box and box != "null":
    b = json.loads(box)
    before = ev("document.querySelector('.alur-edge-head').getAttribute('d')")
    mouse("Pressed", b["x"], b["y"])
    for i in range(1, 6):
        mouse("Moved", b["x"] + i * 22, b["y"] + i * 10)
        time.sleep(0.08)
    mouse("Released", b["x"] + 110, b["y"] + 50)
    time.sleep(1.2)
    after = ev("document.querySelector('.alur-edge-head').getAttribute('d')")
    print("head moved:", before != after, "| hidden:", ev("[...document.querySelectorAll('.alur-edge-head')].filter(h=>h.style.opacity==='0').length"))
else:
    print("no node to move")

ws.close(); proc.terminate()