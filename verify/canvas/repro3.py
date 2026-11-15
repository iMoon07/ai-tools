import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9813
tmp = tempfile.mkdtemp(prefix="diag")
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

SCENE = {
    "module": "canvas", "title": "My canvas", "grid": True, "width": 900, "height": 520,
    "cable": "solid", "motion": "flow", "speed": 1, "selected": "n1",
    "nodes": {"n1": {"id": "n1", "x": 120, "y": 90, "w": 180, "h": 180, "shape": "sticky",
                     "label": "catatan", "fill": "#ffffff", "textColor": "#1971c2", "sloppiness": "artist"}},
    "edges": []
}

cmd("Page.enable"); cmd("Runtime.enable"); cmd("Log.enable")
cmd("Emulation.setDeviceMetricsOverride", width=1400, height=900, deviceScaleFactor=1, mobile=False)
cmd("Page.navigate", url="http://127.0.0.1:8123/draw.html?cb=" + str(time.time()))
time.sleep(3.0)
ev("localStorage.setItem('ruang.scene.v1', %s);" % json.dumps(json.dumps(SCENE)))
cmd("Page.reload", ignoreCache=True)
time.sleep(4.0)

# drain any queued events (exceptions / console)
events = []
c.settimeout(0.6)
try:
    while True:
        events.append(json.loads(c.recv()))
except Exception:
    pass
c.settimeout(30)
for e in events:
    if e.get("method") in ("Runtime.exceptionThrown", "Log.entryAdded"):
        print('EVENT:', json.dumps(e.get("params"))[:400])

print('saved now  :', ev("localStorage.getItem('ruang.scene.v1')")[:220])
print('stage kids :', ev("document.getElementById('stage').children.length"))
print('editorMode :', ev("(function(){var e=document.getElementById('editorMode');return e?e.textContent:'none';})()"))
print('panel title:', ev("(function(){var b=document.querySelector('#shapePanel .shape-head b');return b?b.textContent.trim():'none';})()"))
print('alur       :', ev("[typeof window.Alur, typeof window.AlurKit, typeof window.rough].join(',')"))
print('errs late  :', ev("window.__errs||'not registered'"))
c.close(); proc.terminate()