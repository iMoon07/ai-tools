"""Does the embedded PDF actually paint, and where does the page land after
opening a recognition detail?"""
import base64
import io
import json
import subprocess
import sys
import tempfile
import time
import urllib.request

import websocket

W = int(sys.argv[1]) if len(sys.argv) > 1 else 390
H = int(sys.argv[2]) if len(sys.argv) > 2 else 844
PORT = 9892
tmp = tempfile.mkdtemp(prefix="mob2")
proc = subprocess.Popen([
    "chromium", "--no-sandbox", "--no-first-run", "--no-default-browser-check",
    "--window-position=0,0", "--window-size=%d,%d" % (W + 40, H + 40),
    "--disable-backgrounding-occluded-windows", "--disable-renderer-backgrounding",
    "--remote-debugging-port=%d" % PORT, "--remote-allow-origins=*",
    "--user-data-dir=" + tmp, "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(160):
    try:
        urllib.request.urlopen("http://127.0.0.1:%d/json/version" % PORT, timeout=1).read()
        break
    except Exception:
        time.sleep(0.25)
tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT).read())
c = websocket.create_connection([t for t in tabs if t["type"] == "page"][0]["webSocketDebuggerUrl"], timeout=60)
n = [0]


def cmd(m, **p):
    n[0] += 1
    c.send(json.dumps({"id": n[0], "method": m, "params": p}))
    while True:
        r = json.loads(c.recv())
        if r.get("id") == n[0]:
            return r.get("result", {})


def ev(e):
    r = cmd("Runtime.evaluate", expression=e, returnByValue=True).get("result", {})
    return r.get("value") if r.get("subtype") != "error" else {"__err": str(r.get("description"))[:200]}


def ink(clip):
    from PIL import Image, ImageChops
    data = cmd("Page.captureScreenshot", format="png", clip=dict(clip, scale=1)).get("data", "")
    if not data:
        return "no shot"
    im = Image.open(io.BytesIO(base64.b64decode(data))).convert("L")
    hist = im.histogram()
    dark = sum(hist[:160])
    return {"px": im.size, "dark_ratio": round(dark / float(im.size[0] * im.size[1]), 4)}


try:
    cmd("Page.enable")
    cmd("Runtime.enable")
    cmd("Emulation.setDeviceMetricsOverride", width=W, height=H, deviceScaleFactor=1, mobile=True)
    cmd("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
    cmd("Page.navigate", url="http://127.0.0.1:8123/index.html#about")
    time.sleep(5.0)
    ev("""(function(){document.getElementById('tabExperience').click();})()""")
    time.sleep(0.6)
    ev("""(function(){document.querySelector('[data-open-experience="recognition"]').click();})()""")
    time.sleep(0.6)
    ev("""(function(){document.querySelector('[data-open-experience="recBengkulu"]').click();})()""")
    time.sleep(4.0)

    print("scrollY after open:", ev("Math.round(window.scrollY)"))
    print("detail top:", ev("Math.round(document.getElementById('recBengkuluDetail').getBoundingClientRect().top)"))
    print("back btn top:", ev("Math.round(document.querySelector('#recBengkuluDetail .back-button').getBoundingClientRect().top)"))
    print("pdf internals:", ev("""(function(){
        var f=document.querySelector('#recBengkuluDetail iframe');
        if(!f) return 'no frame';
        var d=f.contentDocument; if(!d) return 'no doc';
        var sr=d.querySelector('pdf-viewer') ? (d.querySelector('pdf-viewer').shadowRoot ? 'shadow' : 'no-shadow') : 'no-viewer';
        return {embeds: d.querySelectorAll('embed').length, viewer: sr,
                bodyLen: d.body ? d.body.innerHTML.length : -1};})()"""))

    f = ev("""(function(){var f=document.querySelector('#recBengkuluDetail iframe');
        var r=f.getBoundingClientRect();
        return {x:Math.round(r.x), y:Math.round(r.y), width:Math.round(r.width), height:Math.round(r.height)};})()""")
    print("frame rect:", f)
    if isinstance(f, dict):
        f = dict(f); f["y"] = max(0, f["y"])
        print("frame ink:", ink(f))
    print("scroll after ink:", ev("Math.round(window.scrollY)"))
finally:
    try:
        c.close()
    except Exception:
        pass
    proc.terminate()