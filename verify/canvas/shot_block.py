import json, subprocess, time, urllib.parse, urllib.request, base64, shutil, os

MD = "http://127.0.0.1:8123/docs/Experiments/foundations/server-architecture/server-single-tier-stack-en.md"
PAGE = "http://127.0.0.1:8123/read.html?url=" + urllib.parse.quote(MD, safe="")
PORT = 9421
PROF = "/tmp/kilo/prof-shot"
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

t = http("/json/new?" + urllib.parse.quote("about:blank", safe=""), method="PUT")
ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
n = [0]
def send(m, **p):
    n[0] += 1
    ws.send(json.dumps({"id": n[0], "method": m, "params": p}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == n[0]:
            if "error" in r: raise RuntimeError(r["error"])
            return r.get("result", {})

send("Page.enable"); send("Runtime.enable")
send("Emulation.setDeviceMetricsOverride", width=1200, height=1000, deviceScaleFactor=2, mobile=False)
send("Page.navigate", url=PAGE)
time.sleep(6)
send("Runtime.evaluate", expression="[...document.querySelectorAll('.topology')][1].scrollIntoView({block:'center'})")
time.sleep(1)
box = send("Runtime.evaluate", expression="""(()=>{const r=[...document.querySelectorAll('.topology')][1].getBoundingClientRect();
return JSON.stringify({x:r.x,y:r.y,w:r.width,h:r.height});})()""", returnByValue=True)["result"]["value"]
b = json.loads(box)
pad = 16
shot = send("Page.captureScreenshot", format="png", captureBeyondViewport=False,
            clip={"x": max(0, b["x"] - pad), "y": max(0, b["y"] - pad),
                  "width": b["w"] + 2 * pad, "height": b["h"] + 2 * pad, "scale": 1})
out = "/tmp/kilo/core-components.png"
open(out, "wb").write(base64.b64decode(shot["data"]))
print(out, os.path.getsize(out), "bytes")
proc.terminate()