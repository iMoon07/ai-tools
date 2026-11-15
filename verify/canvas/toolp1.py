import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9761
tmp=tempfile.mkdtemp(prefix="tlp")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=1400,900","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
for _ in range(80):
    try:
        urllib.request.urlopen("http://127.0.0.1:%d/json/version"%PORT,timeout=1).read(); break
    except Exception: time.sleep(0.25)
tabs=json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json"%PORT).read())
page=[t for t in tabs if t["type"]=="page"][0]
c=websocket.create_connection(page["webSocketDebuggerUrl"],timeout=30)
i=[0]
def cmd(m,**p):
    i[0]+=1; c.send(json.dumps({"id":i[0],"method":m,"params":p}))
    while True:
        r=json.loads(c.recv())
        if r.get("id")==i[0]: return r.get("result",{})
def ev(e):
    r=cmd("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html?cb="+str(time.time())); time.sleep(3.5)
ev("window.__errs=[];window.addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.4)

def ptr(t, x, y, buttons=1):
    ev("(function(){var s=document.getElementById('stage');"
       "s.dispatchEvent(new PointerEvent(" + json.dumps(t) + ",{bubbles:true,cancelable:true,"
       "clientX:%d,clientY:%d,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()"
       % (x, y, buttons))

ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()")
def drag(x0, y0, x1, y1, steps=12):
    ptr("pointerdown", x0, y0)
    for k in range(1, steps + 1):
        ptr("pointermove", x0 + (x1 - x0) * k / steps, y0 + (y1 - y0) * k / steps)
    ptr("pointerup", x1, y1, 0)
    time.sleep(0.5)

def tap(x, y):
    ptr("pointerdown", x, y); ptr("pointerup", x, y, 0); time.sleep(0.45)

# --- sticky note
print('sticky tool', ev("document.querySelector('[data-tool=\"sticky\"]').click() || 'ok'"))
drag(ST['x'] + 200, ST['y'] + 200, ST['x'] + 380, ST['y'] + 380)
print('sticky node', ev("(function(){var S=window._state.spec;var k=Object.keys(S.nodes);"
  "var id=k[k.length-1];var n=S.nodes[id];"
  "var el=document.querySelector('.alur-sticky-node');"
  "return {id:id, shape:n.shape, w:Math.round(n.w), h:Math.round(n.h), fill:n.fill,"
  " el: !!el, path: el?!!el.querySelector('.alur-sticky'):null,"
  " fold: el?!!el.querySelector('.alur-sticky-fold'):null,"
  " shadow: el?!!el.querySelector('.alur-sticky-shadow'):null,"
  " spans: el?el.querySelectorAll('.alur-sticky-label tspan').length:0};})()"))

# type text into it
ev("window._startTextEdit ? null : null")
print('panel', ev("(function(){var h=document.getElementById('shapePanel');"
  "return {hidden:h.hidden, title:(h.querySelector('.shape-head b')||{}).textContent,"
  " secs:[].map.call(h.querySelectorAll('.pp-cap'),function(x){return x.textContent;})};})()"))

# --- fill tool
ev("document.querySelector('[data-tool=\"fill\"]').click()")
time.sleep(0.2)
CEN = ev("(function(){var el=document.querySelector('.alur-sticky-node');var r=el.getBoundingClientRect();"
         "return {x:r.x+r.width/2, y:r.y+r.height/2};})()")
print('centre', CEN)
tap(CEN['x'], CEN['y'])
time.sleep(0.4)
print('fill', ev("(function(){var S=window._state.spec;var id=Object.keys(S.nodes).pop();"
  "var n=S.nodes[id]; return {id:id, shape:n.shape, fill:n.fill, style:n.fillStyle};})()"))

# --- lasso
ev("document.querySelector('[data-tool=\"lasso\"]').click()")
time.sleep(0.2)
# lasso around the sticky note
pts = []
cx, cy = ST['x'] + 290, ST['y'] + 290
import math
ptr("pointerdown", cx + 130, cy)
for k in range(1, 25):
    a = 2 * math.pi * k / 24
    ptr("pointermove", cx + 130 * math.cos(a), cy + 130 * math.sin(a))
ptr("pointerup", cx + 130, cy, 0)
time.sleep(0.5)
print('lasso sel', ev("(function(){var S=window._state.spec;return {sel:S.selected, n:Array.isArray(S.selected)?S.selected.length:0};})()"))
print('errs', ev("window.__errs"))
c.close(); proc.terminate()