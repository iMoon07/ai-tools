"""Certificate cards on mobile: frame height, caption, and the fallback path."""
import json
import subprocess
import sys
import tempfile
import time
import urllib.request

import websocket

W = int(sys.argv[1]) if len(sys.argv) > 1 else 390
MOBILE = len(sys.argv) > 2 and sys.argv[2] == "m"
PORT = 9902
tmp = tempfile.mkdtemp(prefix="pdfcard")
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


try:
    cmd("Page.enable")
    cmd("Runtime.enable")
    cmd("Emulation.setDeviceMetricsOverride", width=W, height=900, deviceScaleFactor=2, mobile=MOBILE)
    cmd("Page.navigate", url="http://127.0.0.1:8123/index.html#about")
    time.sleep(5.0)
    ev("document.getElementById('tabExperience').click()")
    time.sleep(0.6)
    ev("document.querySelector('[data-open-experience=\"recognition\"]').click()")
    time.sleep(0.6)
    ev("document.querySelector('[data-open-experience=\"recBengkulu\"]').click()")
    time.sleep(6.5)

    print("cards:", ev("document.querySelectorAll('#recBengkuluDetail .pdf-card').length"))
    print("frames:", ev("document.querySelectorAll('#recBengkuluDetail .recognition-frame').length"))
    print("captions:", ev("document.querySelectorAll('#recBengkuluDetail .pdf-caption').length"))
    print("open links:", ev("[].slice.call(document.querySelectorAll('#recBengkuluDetail .pdf-open')).map(function(a){return a.getAttribute('href').split('/').pop();})"))
    print("scrollY:", ev("Math.round(window.scrollY)"))
    print("detail top:", ev("Math.round(document.getElementById('recBengkuluDetail').getBoundingClientRect().top)"))
    print("boxes:", ev("""[].slice.call(document.querySelectorAll('#recBengkuluDetail .recognition-frame')).map(function(f){
        var r=f.getBoundingClientRect(); return {w:Math.round(r.width), h:Math.round(r.height)};})"""))
    print("empty cards:", ev("document.querySelectorAll('#recBengkuluDetail .pdf-card.is-empty').length"))
    print("caption text:", ev("(function(){var c=document.querySelector('#recBengkuluDetail .pdf-caption'); return c ? c.innerText.replace(/\\s+/g,' ').trim().slice(0,90) : null;})()"))
    print("overflowX:", ev("[document.documentElement.scrollWidth, innerWidth]"))
finally:
    try:
        c.close()
    except Exception:
        pass
    proc.terminate()