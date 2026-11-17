"""Mobile audit of the Experience > Acknowledged Security Reports panel."""
import json
import subprocess
import sys
import tempfile
import time
import urllib.request

import websocket

W = int(sys.argv[1]) if len(sys.argv) > 1 else 390
H = int(sys.argv[2]) if len(sys.argv) > 2 else 844
URL = sys.argv[3] if len(sys.argv) > 3 else "http://127.0.0.1:8123/index.html"
PORT = 9890
tmp = tempfile.mkdtemp(prefix="mob1")
proc = subprocess.Popen([
    "chromium", "--no-sandbox", "--no-first-run", "--no-default-browser-check",
    "--disable-background-networking", "--window-position=0,0",
    "--window-size=%d,%d" % (W + 40, H + 40),
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


def box(sel):
    return ev("""(function(){var e=document.querySelector(%s); if(!e) return null;
        var r=e.getBoundingClientRect(); var cs=getComputedStyle(e);
        return {x:Math.round(r.x), y:Math.round(r.y), w:Math.round(r.width), h:Math.round(r.height),
                fs:cs.fontSize, disp:cs.display};})()""" % json.dumps(sel))


try:
    cmd("Page.enable")
    cmd("Runtime.enable")
    cmd("Emulation.setDeviceMetricsOverride", width=W, height=H, deviceScaleFactor=2, mobile=True)
    cmd("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
    cmd("Page.navigate", url=URL + "#about")
    time.sleep(5.0)
    print("viewport:", ev("({w: innerWidth, h: innerHeight, dpr: devicePixelRatio})"))
    print("doc scrollW/clientW:", ev("[document.documentElement.scrollWidth, document.documentElement.clientWidth]"))
    print("tabs:", ev("[].slice.call(document.querySelectorAll('.tab')).map(function(t){return t.textContent.trim();})"))
    print("open Experience:", ev("""(function(){var t=document.getElementById('tabExperience');
        if(!t) return 'no tab'; t.click(); return 'clicked';})()"""))
    time.sleep(0.8)
    print("panel visible:", ev("(function(){var p=document.getElementById('panelExperience'); return p? !p.hidden : 'none';})()"))
    print("open Recognition:", ev("""(function(){var b=document.querySelector('[data-open-experience="recognition"]');
        if(!b) return 'no entry'; b.click(); return 'clicked';})()"""))
    time.sleep(0.8)
    print("rows:", ev("document.querySelectorAll('#recognitionDetail .experience-entry').length"))
    print("list box:", box("#recognitionDetail .recognition-list"))
    print("row name fs:", box("#recognitionDetail .experience-name"))
    print("row desc fs:", box("#recognitionDetail .experience-description"))
    print("open Bengkulu:", ev("""(function(){var b=document.querySelector('[data-open-experience="recBengkulu"]');
        if(!b) return 'no entry'; b.click(); return 'clicked';})()"""))
    time.sleep(2.0)
    print("detail visible:", ev("(function(){var d=document.getElementById('recBengkuluDetail'); return d? !d.hidden : 'none';})()"))
    print("doc scrollW/clientW:", ev("[document.documentElement.scrollWidth, document.documentElement.clientWidth]"))
    print("preview box:", box("#recBengkuluDetail .recognition-preview"))
    print("frames:", ev("""[].slice.call(document.querySelectorAll('#recBengkuluDetail iframe')).map(function(f){
        var r=f.getBoundingClientRect();
        var d=null; try { d = f.contentDocument ? f.contentDocument.documentElement.outerHTML.slice(0,160) : 'no doc'; } catch(e){ d='err '+e.name; }
        return {w:Math.round(r.width), h:Math.round(r.height), src:f.getAttribute('src').slice(-42), doc:d};})"""))
    print("frame natural size:", ev("""(function(){var f=document.querySelector('#recBengkuluDetail iframe');
        return f ? {attrW:f.getAttribute('width'), attrH:f.getAttribute('height')} : null;})()"""))
    print("back btn:", box("#recBengkuluDetail .back-button"))
    print("title:", box("#recBengkuluDetail .detail-title"))
    print("h overflow elements:", ev("""[].slice.call(document.querySelectorAll('body *')).filter(function(e){
        var r=e.getBoundingClientRect(); return r.width>0 && (r.right > innerWidth + 1 || r.left < -1);})
        .slice(0,8).map(function(e){return (e.className||e.tagName)+':'+Math.round(e.getBoundingClientRect().right);})"""))
    print("screenshot bytes:", len(cmd("Page.captureScreenshot", format="png").get("data", "")))
finally:
    try:
        c.close()
    except Exception:
        pass
    proc.terminate()