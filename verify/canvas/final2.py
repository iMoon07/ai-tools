import json, time, urllib.request, subprocess, tempfile
import websocket

PORT = 9801
tmp = tempfile.mkdtemp(prefix="final")
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
ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y};})()")
def ptr(t, x, y, b=1):
    ev("(function(){var s=document.getElementById('stage');s.dispatchEvent(new PointerEvent(" + json.dumps(t) +
       ",{bubbles:true,cancelable:true,clientX:%d,clientY:%d,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()" % (x, y, b))
def drag(x0, y0, x1, y1):
    ptr("pointerdown", x0, y0)
    for k in range(1, 11):
        ptr("pointermove", x0 + (x1 - x0) * k / 10, y0 + (y1 - y0) * k / 10)
    ptr("pointerup", x1, y1, 0); time.sleep(0.6)
def panel():
    return ev("(function(){var b=document.querySelector('#shapePanel .shape-head b');"
              "var caps=[];document.querySelectorAll('#shapePanel .pp-cap').forEach(function(x){caps.push(x.textContent.trim());});"
              "return (b?b.textContent.trim():'hidden')+' :: '+caps.join('|');})()")

print('== sticky via TOOL (no inline editor) ==')
ev("document.querySelector('[data-tool=\"sticky\"]').click()")
drag(ST['x'] + 260, ST['y'] + 180, ST['x'] + 380, ST['y'] + 300)
print('  panel:', panel())
print('  dots :', ev("document.querySelectorAll('#shapePanel .pp-dot').length"))
ev("(function(){var d=document.querySelectorAll('#shapePanel .pp-sw')[1];d.querySelectorAll('.pp-dot')[3].click();})()")
time.sleep(0.6)
print('  after Ink click:', panel())
print('  spec ink:', ev("(function(){var s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));"
                      "var k=null;Object.keys(s.nodes).forEach(function(x){if(s.nodes[x].shape==='sticky')k=x;});return s.nodes[k].textColor;})()"))

print('== sticky via KEY N (inline editor open) ==')
ev("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'n',bubbles:true,cancelable:true}));")
time.sleep(0.9)
print('  textEdit:', ev("!!document.getElementById('inlineText')"))
print('  panel   :', panel())
print('  dots    :', ev("document.querySelectorAll('#shapePanel .pp-dot').length"))
ev("(function(){var d=document.querySelectorAll('#shapePanel .pp-sw')[0];d.querySelectorAll('.pp-dot')[3].click();})()")
time.sleep(0.6)
print('  after Paper click:', panel())
print('  dots now:', ev("document.querySelectorAll('#shapePanel .pp-dot').length"))

print('== fill tool ==')
ev("document.querySelector('[data-tool=\"fill\"]').click()")
time.sleep(0.6)
print('  panel:', panel())
print('  dots :', ev("document.querySelectorAll('#shapePanel .pp-dot').length"))

print('errs:', ev("window.__errs"))
c.close(); proc.terminate()