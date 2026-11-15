import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9785
tmp = tempfile.mkdtemp(prefix="fx")
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

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride", width=1400, height=900, deviceScaleFactor=1, mobile=False)
cmd("Page.navigate", url="http://127.0.0.1:8123/draw.html?cb=" + str(time.time()))
time.sleep(3.6)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)

def ptr(t, x, y, buttons=1):
    ev("(function(){var s=document.getElementById('stage');"
       "s.dispatchEvent(new PointerEvent(" + json.dumps(t) + ",{bubbles:true,cancelable:true,"
       "clientX:%d,clientY:%d,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()" % (x, y, buttons))
ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y};})()")
def drag(x0, y0, x1, y1, steps=10):
    ptr("pointerdown", x0, y0)
    for k in range(1, steps + 1):
        ptr("pointermove", x0 + (x1 - x0) * k / steps, y0 + (y1 - y0) * k / steps)
    ptr("pointerup", x1, y1, 0); time.sleep(0.5)

ev("document.querySelector('[data-tool=\"box\"]').click()")
drag(ST['x'] + 200, ST['y'] + 200, ST['x'] + 360, ST['y'] + 300)
ev("(function(){var i=document.querySelector('#shapePanel .pp-link input');i.value='example.com';"
   "var b=document.querySelectorAll('#shapePanel .pp-link button');if(b[0])b[0].click();})()")
time.sleep(0.7)
print('spec:', ev("(function(){return document.getElementById('stage').getAttribute('data-spec');})()")[:400])
print('link els:', ev("document.querySelectorAll('.alur-node-link').length"))
print('selected:', ev("(function(){var g=document.querySelector('.alur-canvas-node.is-selected');return g?g.getAttribute('data-node-id'):null;})()"))
# deselect through the select tool + empty tap
ev("document.querySelector('[data-tool=\"select\"]').click()")
time.sleep(0.3)
ptr("pointerdown", ST['x'] + 1100, ST['y'] + 700)
ptr("pointerup", ST['x'] + 1100, ST['y'] + 700, 0)
time.sleep(0.6)
print('selected after tap:', ev("(function(){var g=document.querySelector('.alur-canvas-node.is-selected');return g?g.getAttribute('data-node-id'):null;})()"))
print('link els after deselect:', ev("document.querySelectorAll('.alur-node-link').length"))
print('errs:', ev("window.__errs"))
c.close(); proc.terminate()