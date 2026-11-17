"""Check the row logos: pseudo-element size, resolved image, and that it loads."""
import json
import subprocess
import sys
import tempfile
import time
import urllib.request

import websocket

W = int(sys.argv[1]) if len(sys.argv) > 1 else 390
MOBILE = len(sys.argv) > 2 and sys.argv[2] == "m"
PORT = 9896
tmp = tempfile.mkdtemp(prefix="logos1")
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


SEL = '[data-open-experience="merdeka"], [data-open-experience="xcode"], [data-open-experience="lpro"], [data-open-community="codingceria"]'
try:
    cmd("Page.enable")
    cmd("Runtime.enable")
    cmd("Network.enable")
    cmd("Emulation.setDeviceMetricsOverride", width=W, height=900, deviceScaleFactor=2, mobile=MOBILE)
    cmd("Page.navigate", url="http://127.0.0.1:8123/index.html#about")
    time.sleep(5.0)
    print("rows found:", ev("document.querySelectorAll(%s).length" % json.dumps(SEL)))
    print("boxes:", ev("""(function(){
        return [].slice.call(document.querySelectorAll(%s)).map(function(b){
            var cs=getComputedStyle(b,'::before');
            var w=parseFloat(cs.width), h=parseFloat(cs.height);
            return {key: b.dataset.openExperience || b.dataset.openCommunity,
                    w: Math.round(w), h: Math.round(h),
                    img: (cs.backgroundImage||'').split('url("')[1] ? cs.backgroundImage.split('url("')[1].split('"')[0] : '',
                    content: cs.content};});})()""" % json.dumps(SEL)))
    print("loaded imgs:", ev("""(function(){
        return performance.getEntriesByType('resource')
            .filter(function(r){return r.name.indexOf('/assets/brand/') >= 0;})
            .map(function(r){return r.name.split('/').pop() + ' ' + Math.round(r.transferSize||0) + 'B';});})()"""))
finally:
    try:
        c.close()
    except Exception:
        pass
    proc.terminate()