import json, subprocess, time, urllib.parse, urllib.request, shutil

PORT = 9451
PROF = "/tmp/alur-probes/prof-arrow"
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
    if res.get("subtype") == "error":
        return "ERR " + str(res.get("description"))[:200]
    return res.get("value")

send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride", width=1400, height=1000, deviceScaleFactor=1, mobile=False)
send("Page.navigate", url="http://127.0.0.1:8123/draw.html")
time.sleep(4)

ev("document.querySelector('[data-scene-module=flow]').click()")
time.sleep(2)

probe = """(()=>{
  const hs = [...document.querySelectorAll('.alur-edge-head')];
  const svg = document.querySelector('#stage svg');
  const svgBox = svg ? svg.getBoundingClientRect() : null;
  return JSON.stringify({
    count: hs.length,
    edges: document.querySelectorAll('.alur-cable').length,
    svgBox: svgBox ? [Math.round(svgBox.x), Math.round(svgBox.y), Math.round(svgBox.width), Math.round(svgBox.height)] : null,
    heads: hs.slice(0,4).map(h => {
      const r = h.getBoundingClientRect();
      const cs = getComputedStyle(h);
      return {
        d: (h.getAttribute('d')||'').slice(0,40),
        stroke: cs.stroke, sw: cs.strokeWidth, op: cs.opacity,
        vis: cs.visibility, disp: cs.display,
        bbox: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
        inViewport: r.width > 0 && r.height > 0
      };
    })
  });
})()"""

for i in range(6):
    print(i, ev(probe))
    time.sleep(0.4)

print("after 3s idle:")
time.sleep(3)
print(" ", ev(probe))

print("motion none:")
ev("""(()=>{const s=JSON.parse(document.getElementById('spec').value);
 s.motion='none'; document.getElementById('spec').value=JSON.stringify(s,null,2);
 document.getElementById('apply').click(); return 1;})()""")
time.sleep(2)
print(" ", ev(probe))

ws.close(); proc.terminate()