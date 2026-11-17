"""Row logos: count, gap to the text, and whether the images load."""
import json
import subprocess
import sys
import tempfile
import time
import urllib.request

import websocket

W = int(sys.argv[1]) if len(sys.argv) > 1 else 390
MOBILE = len(sys.argv) > 2 and sys.argv[2] == "m"
TAB = sys.argv[3] if len(sys.argv) > 3 else "tabExperience"
PORT = 9897
tmp = tempfile.mkdtemp(prefix="logos2")
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


SEL = ('[data-open-experience="merdeka"], [data-open-experience="xcode"], '
       '[data-open-experience="lpro"], [data-open-community="debuglife"], '
       '[data-open-community="codelines"], [data-open-community="codingceria"]')
try:
    cmd("Page.enable")
    cmd("Runtime.enable")
    cmd("Emulation.setDeviceMetricsOverride", width=W, height=900, deviceScaleFactor=2, mobile=MOBILE)
    cmd("Page.navigate", url="http://127.0.0.1:8123/index.html#about")
    time.sleep(5.0)
    ev("\n(function(){var t=document.getElementById('%s'); if(t) t.click();})()".replace('%s', TAB))
    time.sleep(0.8)
    print("viewport:", ev("[innerWidth, document.documentElement.clientWidth]"))
    print("logo rows:", ev("document.querySelectorAll(%s).length" % json.dumps(SEL)))
    print("layout:", ev("""(function(){
        return [].slice.call(document.querySelectorAll(%s)).map(function(b){
            var cs = getComputedStyle(b, '::before');
            var before = {w: parseFloat(cs.width), img: (cs.backgroundImage||'').split('/').pop().replace(/[\\)"']/g,'')};
            var text = b.querySelector('span');
            var arrow = b.querySelector('.experience-arrow');
            var br = b.getBoundingClientRect();
            var tr = text ? text.getBoundingClientRect() : null;
            var ar = arrow ? arrow.getBoundingClientRect() : null;
            return {key: b.dataset.openExperience || b.dataset.openCommunity,
                    logo: before.w, img: before.img,
                    gapToText: tr ? Math.round(tr.left - (br.left + before.w)) : null,
                    arrowRightGap: ar ? Math.round(br.right - ar.right) : null,
                    rowH: Math.round(br.height)};});})()""" % json.dumps(SEL)))
    print("loaded:", ev("""performance.getEntriesByType('resource')
        .filter(function(r){return r.name.indexOf('/assets/brand/') >= 0;})
        .map(function(r){return r.name.split('/').pop();})"""))
    print("overflowX:", ev("[document.documentElement.scrollWidth, innerWidth]"))
finally:
    try:
        c.close()
    except Exception:
        pass
    proc.terminate()