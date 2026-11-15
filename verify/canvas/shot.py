import json, time, urllib.request, subprocess, tempfile, base64
import websocket

PORT = 9824
tmp = tempfile.mkdtemp(prefix="shot")
proc = subprocess.Popen(["chromium", "--headless=new", "--disable-gpu", "--no-sandbox",
    "--hide-scrollbars", "--remote-debugging-port=%d" % PORT, "--remote-allow-origins=*",
    "--user-data-dir=" + tmp, "--window-size=1400,900", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(80):
    try:
        urllib.request.urlopen("http://127.0.0.1:%d/json/version" % PORT, timeout=1).read(); break
    except Exception:
        time.sleep(0.25)
tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT).read())
page = [t for t in tabs if t["type"] == "page"][0]
c = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=30)
i = [0]
def cmd(m, **p):
    i[0] += 1; c.send(json.dumps({"id": i[0], "method": m, "params": p}))
    while True:
        r = json.loads(c.recv())
        if r.get("id") == i[0]: return r.get("result", {})
def ev(e):
    r = cmd("Runtime.evaluate", expression=e, returnByValue=True, awaitPromise=True).get("result", {})
    return r.get("value") if r.get("subtype") != "error" else {"__err": r.get("description")}

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride", width=1400, height=900, deviceScaleFactor=1, mobile=False)
cmd("Page.navigate", url="http://127.0.0.1:8123/draw.html?cb=" + str(time.time()))
time.sleep(3.6)
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)
ev("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'n',bubbles:true,cancelable:true}));")
time.sleep(1.0)
ev("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));")
time.sleep(0.6)
box = ev("(function(){var p=document.querySelector('.alur-sticky');if(!p)return null;"
         "var r=p.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()")
print('sticky box:', box)
if box:
    pad = 70
    clip = {"x": max(0, box["x"] - pad), "y": max(0, box["y"] - pad),
            "width": box["w"] + pad * 2, "height": box["h"] + pad * 2, "scale": 2}
    data = cmd("Page.captureScreenshot", format="png", clip=clip).get("data")
    open("/tmp/alur-probes/sticky.png", "wb").write(base64.b64decode(data))
    print('saved /tmp/alur-probes/sticky.png')
c.close(); proc.terminate()