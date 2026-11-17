"""PDF paint check: same page at desktop vs mobile emulation."""
import base64
import io
import json
import subprocess
import sys
import tempfile
import time
import urllib.request

import websocket

W = int(sys.argv[1])
H = int(sys.argv[2])
MOBILE = sys.argv[3] == "m"
PORT = 9893 + (1 if MOBILE else 0)
tmp = tempfile.mkdtemp(prefix="pdf3")
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


try:
    cmd("Page.enable")
    cmd("Runtime.enable")
    cmd("Emulation.setDeviceMetricsOverride", width=W, height=H, deviceScaleFactor=1, mobile=MOBILE)
    if MOBILE:
        cmd("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
    cmd("Page.navigate", url="http://127.0.0.1:8123/index.html#about")
    time.sleep(5.0)
    print("about page shown:", ev("!document.getElementById('aboutPage').hidden"))
    print("tabs:", ev("document.querySelectorAll('.tab').length"))
    print("click exp:", ev("(function(){var t=document.getElementById('tabExperience'); t.click(); return !document.getElementById('panelExperience').hidden;})()"))
    time.sleep(0.5)
    print("recognition:", ev("(function(){var b=document.querySelector('[data-open-experience=\"recognition\"]'); if(!b) return 'none'; b.click(); return !document.getElementById('recognitionDetail').hidden;})()"))
    time.sleep(0.5)
    print("bengkulu:", ev("(function(){var b=document.querySelector('[data-open-experience=\"recBengkulu\"]'); if(!b) return 'none'; b.click(); return !document.getElementById('recBengkuluDetail').hidden;})()"))
    time.sleep(5.0)
    print("frame box:", ev("""(function(){var f=document.querySelector('#recBengkuluDetail iframe');
        if(!f) return null; var r=f.getBoundingClientRect();
        return {x:Math.round(r.x), y:Math.round(r.y), w:Math.round(r.width), h:Math.round(r.height)};})()"""))
    print("pdf internals:", ev("""(function(){var f=document.querySelector('#recBengkuluDetail iframe');
        var d=f && f.contentDocument; if(!d) return 'no doc';
        return {embeds:d.querySelectorAll('embed').length, object:d.querySelectorAll('object').length,
                viewer:!!d.querySelector('pdf-viewer'), bodyLen:d.body?d.body.innerHTML.length:-1,
                bodyText:(d.body?d.body.innerText:'').slice(0,80)};})()"""))
    f = ev("""(function(){var f=document.querySelector('#recBengkuluDetail iframe');
        var r=f.getBoundingClientRect(); return {x:Math.round(r.x), y:Math.max(0,Math.round(r.y)),
        width:Math.round(r.width), height:Math.round(r.height)};})()""")
    if isinstance(f, dict) and f["width"] > 0:
        from PIL import Image
        data = cmd("Page.captureScreenshot", format="png", clip=dict(f, scale=1)).get("data", "")
        im = Image.open(io.BytesIO(base64.b64decode(data))).convert("L")
        h = im.histogram()
        print("frame ink dark_ratio:", round(sum(h[:160]) / float(im.size[0] * im.size[1]), 4),
              "| white_ratio:", round(sum(h[240:]) / float(im.size[0] * im.size[1]), 4))
finally:
    try:
        c.close()
    except Exception:
        pass
    proc.terminate()