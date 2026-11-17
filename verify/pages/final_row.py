"""Final pass: row logos, spacing, and console errors at phone and desktop."""
import json
import subprocess
import sys
import tempfile
import time
import urllib.request

import websocket

W = int(sys.argv[1]) if len(sys.argv) > 1 else 390
MOBILE = len(sys.argv) > 2 and sys.argv[2] == "m"
PORT = 9910
tmp = tempfile.mkdtemp(prefix="finalrow")
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
errors = []


def cmd(m, **p):
    n[0] += 1
    c.send(json.dumps({"id": n[0], "method": m, "params": p}))
    while True:
        msg = json.loads(c.recv())
        if msg.get("method") == "Runtime.exceptionThrown":
            d = msg["params"]["exceptionDetails"]
            errors.append((d.get("text") or "") + " " + str(d.get("exception", {}).get("description", ""))[:120])
        if msg.get("id") == n[0]:
            return msg.get("result", {})


def ev(e):
    r = cmd("Runtime.evaluate", expression=e, returnByValue=True).get("result", {})
    return r.get("value") if r.get("subtype") != "error" else {"__err": str(r.get("description"))[:200]}


ROWS = [('experience', 'merdeka'), ('experience', 'xcode'), ('experience', 'lpro'),
        ('community', 'debuglife'), ('community', 'codelines'), ('community', 'codingceria')]
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
        time.sleep(0.6)
        out = ev("""(function(){var b=document.querySelector('[%s="%s"]');
            if(!b) return null; var q=b.getBoundingClientRect();
            var cs=getComputedStyle(b,'::before');
            var text=b.querySelector('span'); var arrow=b.querySelector('.experience-arrow');
            var tr=text.getBoundingClientRect(); var ar=arrow?arrow.getBoundingClientRect():null;
            return {logo: Math.round(parseFloat(cs.width)),
                    img: (cs.backgroundImage||'').split('/').pop().replace(/[\\"')]/g,''),
                    gap: Math.round(tr.left-(q.left+parseFloat(cs.width))),
                    arrowGap: ar?Math.round(q.right-ar.right):null,
                    h: Math.round(q.height),
                    clipped: tr.right > q.right + 1};})()""" % (attr, key))
        print("%-12s %s" % (key, out))

    ev("(function(){var t=document.getElementById('tabExperience'); if(t) t.click();})()")
    time.sleep(0.6)
    print("overflow:", ev("[document.documentElement.scrollWidth, innerWidth]"))
    print("errors:", errors[:4])
finally:
    try:
        c.close()
    except Exception:
        pass
    proc.terminate()