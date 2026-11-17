"""Measure every row logo tile: size, ink coverage, and whether it is blank."""
import base64
import io
import json
import subprocess
import sys
import tempfile
import time
import urllib.request

import websocket
from PIL import Image, ImageChops

W = int(sys.argv[1]) if len(sys.argv) > 1 else 1280
MOBILE = len(sys.argv) > 2 and sys.argv[2] == "m"
PORT = 9900
tmp = tempfile.mkdtemp(prefix="logos3")
proc = subprocess.Popen([
    "chromium", "--no-sandbox", "--no-first-run", "--no-default-browser-check",
    "--window-position=0,0", "--window-size=%d,900" % (W + 40),
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


ROWS = [("experience", "merdeka"), ("experience", "xcode"), ("experience", "lpro"),
        ("community", "debuglife"), ("community", "codelines"), ("community", "codingceria")]

try:
    cmd("Page.enable")
    cmd("Runtime.enable")
    cmd("Emulation.setDeviceMetricsOverride", width=W, height=900, deviceScaleFactor=2, mobile=MOBILE)
    cmd("Page.navigate", url="http://127.0.0.1:8123/index.html#about")
    time.sleep(5.0)

    for panel, key in ROWS:
        attr = "data-open-experience" if panel == "experience" else "data-open-community"
        tab = "tabExperience" if panel == "experience" else "tabCommunity"
        ev("(function(){var t=document.getElementById('%s'); if(t) t.click();})()" % tab)
        time.sleep(0.8)
        ev("(function(){window.scrollTo(0,0);})()")
        time.sleep(0.3)
        r = ev("""(function(){var b=document.querySelector('[%s="%s"]');
            if(!b) return null; b.scrollIntoView({block:'center'});
            var q=b.getBoundingClientRect();
            return {x:Math.round(q.x), y:Math.round(q.y + window.scrollY), width:80, height:48};})()""" % (attr, key))
        time.sleep(0.6)
        r = ev("""(function(){var b=document.querySelector('[%s="%s"]');
            var q=b.getBoundingClientRect();
            return {x:Math.round(q.x), y:Math.round(q.y + window.scrollY), width:80, height:48};})()""" % (attr, key))
        if not r:
            print("%-11s no row" % key)
            continue
        data = cmd("Page.captureScreenshot", format="png").get("data", "")
        im = Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB")
        dpr = im.size[0] / float(ev("innerWidth"))
        im = im.crop((int(r["x"] * dpr), int(r["y"] * dpr), int((r["x"] + r["width"]) * dpr), int((r["y"] + r["height"]) * dpr)))
        bg = im.getpixel((1, 1))
        diff = ImageChops.difference(im, Image.new("RGB", im.size, bg)).convert("L")
        ink = sum(1 for v in diff.get_flattened_data() if v > 25) / float(im.size[0] * im.size[1]) * 100
        print("%-11s tile %dx%d  ink %5.1f%%  bg %s" % (key, im.size[0] // 2, im.size[1] // 2, ink, bg))
finally:
    try:
        c.close()
    except Exception:
        pass
    proc.terminate()