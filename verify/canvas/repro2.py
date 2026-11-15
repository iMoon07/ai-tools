import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9812
tmp = tempfile.mkdtemp(prefix="saved")
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
def real_click(x, y):
    for kind, buttons in (("mousePressed", 1), ("mouseReleased", 0)):
        cmd("Input.dispatchMouseEvent", type=kind, x=x, y=y, button="left", buttons=buttons, clickCount=1)
        time.sleep(0.06)
    time.sleep(0.55)

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride", width=1400, height=900, deviceScaleFactor=1, mobile=False)

SCENE = {
    "module": "canvas", "title": "My canvas", "grid": True, "width": 900, "height": 520,
    "cable": "solid", "motion": "flow", "speed": 1,
    "selected": "n1",
    "nodes": {
        "n1": {"id": "n1", "x": 120, "y": 90, "w": 180, "h": 180, "shape": "sticky",
               "label": "catatan", "fill": "#ffffff", "textColor": "#1971c2", "sloppiness": "artist"}
    },
    "edges": []
}

cmd("Page.navigate", url="http://127.0.0.1:8123/draw.html?cb=" + str(time.time()))
time.sleep(3.0)
ev("localStorage.setItem('ruang.scene.v1', %s);" % json.dumps(json.dumps(SCENE)))
cmd("Page.reload", ignoreCache=True)
time.sleep(3.8)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.4)

print('loaded fill:', ev("(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));"
                         "return s.nodes.n1.fill+' / '+s.nodes.n1.textColor+' / inkDefault='+s.inkDefault;})()"))
print('panel:', ev("(function(){var b=document.querySelector('#shapePanel .shape-head b');"
                   "return b?b.textContent.trim():'hidden';})()"))
print('hex:', ev("(function(){var o=[];document.querySelectorAll('#shapePanel .pp-hex').forEach(function(h){o.push(h.value);});return o.join(' , ');})()"))
print('pressed:', ev("(function(){var o=[];document.querySelectorAll('#shapePanel .pp-dot[aria-pressed=\"true\"]')"
                     ".forEach(function(b){o.push(b.dataset.color);});return o.join(' , ');})()"))

print('\n-- click YELLOW Paper dot with real mouse --')
pos = ev("(function(){var d=document.querySelectorAll('#shapePanel .pp-sw')[0];"
         "var b=d.querySelectorAll('.pp-dot')[0];var r=b.getBoundingClientRect();"
         "var cx=Math.round(r.x+r.width/2),cy=Math.round(r.y+r.height/2);"
         "var t=document.elementFromPoint(cx,cy);"
         "return JSON.stringify({x:cx,y:cy,top:t?t.tagName+'.'+(t.className||''):'null'});})()")
print('pos:', pos)
q = json.loads(pos)
real_click(q['x'], q['y'])
time.sleep(0.7)
print('after fill:', ev("(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));"
                        "return s.nodes.n1.fill;})()"))
print('after hex :', ev("(function(){var o=[];document.querySelectorAll('#shapePanel .pp-hex').forEach(function(h){o.push(h.value);});return o.join(' , ');})()"))
print('errs:', ev("window.__errs"))
c.close(); proc.terminate()