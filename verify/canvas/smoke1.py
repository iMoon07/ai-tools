import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9765
tmp=tempfile.mkdtemp(prefix="smk")
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
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html?cb="+str(time.time())); time.sleep(3.4)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)
print('hooks removed:', ev("[typeof window._state, typeof window._editor, typeof window._render].join(',')"))
print('rough lib:', ev("typeof window.rough"))

def ptr(t, x, y, buttons=1):
    ev("(function(){var s=document.getElementById('stage');"
       "s.dispatchEvent(new PointerEvent(" + json.dumps(t) + ",{bubbles:true,cancelable:true,"
       "clientX:%d,clientY:%d,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()"
       % (x, y, buttons))

ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y};})()")
def drag(x0, y0, x1, y1, steps=10):
    ptr("pointerdown", x0, y0)
    for k in range(1, steps + 1):
        ptr("pointermove", x0 + (x1 - x0) * k / steps, y0 + (y1 - y0) * k / steps)
    ptr("pointerup", x1, y1, 0)
    time.sleep(0.45)
def tap(x, y):
    ptr("pointerdown", x, y); ptr("pointerup", x, y, 0); time.sleep(0.4)

# draw a box, select it, roughen it, recolour it, duplicate, delete
ev("document.querySelector('[data-tool=\"box\"]').click()")
drag(ST['x'] + 180, ST['y'] + 180, ST['x'] + 360, ST['y'] + 280)
tap(ST['x'] + 270, ST['y'] + 230)
print('panel title', ev("(function(){var b=document.querySelector('#shapePanel .shape-head b');return b?b.textContent.trim():null;})()"))
ev("(function(){var ss=document.querySelectorAll('#shapePanel .pp-sec');"
   "for(var i=0;i<ss.length;i++){var c=ss[i].querySelector('.pp-cap');"
   "if(c&&c.textContent.trim().indexOf('Roughness')===0) ss[i].querySelectorAll('.pp-seg button')[1].click();}})()")
time.sleep(0.5)
print('rough paths after artist', ev("document.querySelectorAll('.alur-node-rough').length"))
ev("(function(){var p=document.querySelector('.pp-custom'); if(p) p.click();})()")
time.sleep(0.3)
ev("(function(){var p=document.querySelector('.color-pop'); if(p) p.querySelectorAll('.pal .swatch')[4].click();})()")
time.sleep(0.5)
print('panel after recolour', ev("!!document.querySelector('#shapePanel .pp-dot[aria-pressed=\"true\"]')"))
# pen stroke still works and is not a laser
ev("document.querySelector('[data-tool=\"draw\"]').click()")
drag(ST['x'] + 500, ST['y'] + 500, ST['x'] + 640, ST['y'] + 560, 12)
print('pen drawings', ev("(function(){return document.querySelectorAll('.alur-drawing').length;})()"))
print('pen has no laser class', ev("(function(){return document.querySelectorAll('.alur-drawing .alur-laser-path, .alur-drawing.laser').length;})()"))

# eraser over the pen stroke
ev("document.querySelector('[data-tool=\"eraser\"]').click()")
for k in range(1, 9):
    tap(ST['x'] + 500 + k * 18, ST['y'] + 500 + k * 8)
time.sleep(0.5)
print('drawings after erase', ev("(function(){return document.querySelectorAll('.alur-drawing').length;})()"))

# laser still distinct after all this
ev("document.querySelector('[data-tool=\"laser\"]').click()")
drag(ST['x'] + 200, ST['y'] + 650, ST['x'] + 420, ST['y'] + 700, 10)
print('laser layers', ev("document.querySelectorAll('.alur-laser-path').length"))
print('errs', ev("window.__errs"))
c.close(); proc.terminate()