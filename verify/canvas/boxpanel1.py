import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9799
tmp = tempfile.mkdtemp(prefix="box")
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
        time.sleep(0.05)
    time.sleep(0.55)

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride", width=1400, height=900, deviceScaleFactor=1, mobile=False)
cmd("Page.navigate", url="http://127.0.0.1:8123/draw.html?cb=" + str(time.time()))
time.sleep(3.6)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)

def ptr(t, x, y, b=1):
    ev("(function(){var s=document.getElementById('stage');s.dispatchEvent(new PointerEvent(" + json.dumps(t) +
       ",{bubbles:true,cancelable:true,clientX:%d,clientY:%d,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()" % (x, y, b))
ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y};})()")
ev("document.querySelector('[data-tool=\"box\"]').click()")
ptr("pointerdown", ST['x'] + 620, ST['y'] + 480)
ptr("pointermove", ST['x'] + 700, ST['y'] + 540)
ptr("pointerup", ST['x'] + 780, ST['y'] + 600, 0)
time.sleep(0.7)

print('title:', ev("(function(){var b=document.querySelector('#shapePanel .shape-head b');return b?b.textContent.trim():null;})()"))
print('caps:', ev("(function(){var o=[];document.querySelectorAll('#shapePanel .pp-cap').forEach(function(x){o.push(x.textContent.trim());});return o.join('|');})()"))
print('actions:', ev("(function(){var o=[];document.querySelectorAll('#shapePanel .pp-acts .pp-txt').forEach(function(x){o.push(x.textContent);});return o.join('|');})()"))
print('link field:', ev("!!document.querySelector('#shapePanel .pp-link input')"))
print('roughness seg:', ev("document.querySelectorAll('#shapePanel .pp-seg').length"))
print('opacity:', ev("!!document.querySelector('#shapePanel .pp-range')"))
print('errs:', ev("window.__errs"))
c.close(); proc.terminate()