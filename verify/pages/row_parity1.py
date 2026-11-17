"""Layout parity: logo rows are tight, the other rows keep the old geometry."""
import json
import subprocess
import sys
import tempfile
import time
import urllib.request

import websocket

W = int(sys.argv[1]) if len(sys.argv) > 1 else 390
MOBILE = len(sys.argv) > 2 and sys.argv[2] == "m"
PORT = 9914
tmp = tempfile.mkdtemp(prefix="parityrow")
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


JS = """(function(){
  function row(sel){
    var b=document.querySelector(sel); if(!b) return null;
    var q=b.getBoundingClientRect(), cs=getComputedStyle(b,'::before');
    var text=b.querySelector('span'), arrow=b.querySelector('.experience-arrow');
    var tr=text.getBoundingClientRect(), ar=arrow?arrow.getBoundingClientRect():null;
    return {logo: Math.round(parseFloat(cs.width)),
            content: cs.content,
            justify: getComputedStyle(b).justifyContent,
            textLeft: Math.round(tr.left - q.left),
            arrowGap: ar ? Math.round(q.right - ar.right) : null,
            textW: Math.round(tr.width),
            h: Math.round(q.height)};
  }
  return {merdeka: row('[data-open-experience="merdeka"]'),
          recognitionRow: row('[data-open-experience="recognition"]'),
          recBengkulu: row('[data-open-experience="recBengkulu"]'),
          recPrague: row('[data-open-experience="recPrague"]')};
})()"""

try:
    cmd("Page.enable")
    cmd("Runtime.enable")
    cmd("Emulation.setDeviceMetricsOverride", width=W, height=900, deviceScaleFactor=2, mobile=MOBILE)
    cmd("Page.navigate", url="http://127.0.0.1:8123/index.html#about")
    time.sleep(5.0)
    ev("document.getElementById('tabExperience').click()")
    time.sleep(0.8)
    print("experience:", json.dumps(ev(JS)))
    ev("document.querySelector('[data-open-experience=\"recognition\"]').click()")
    time.sleep(0.8)
    print("recognition list:", json.dumps(ev(JS)))
    print("inner rows:", ev("document.querySelectorAll('#recognitionDetail .experience-entry').length"))
    print("overflow:", ev("[document.documentElement.scrollWidth, innerWidth]"))
finally:
    try:
        c.close()
    except Exception:
        pass
    proc.terminate()