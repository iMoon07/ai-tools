import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9759
tmp=tempfile.mkdtemp(prefix="lzp")
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

SNAP = """(function(){
  var g=document.querySelector('.alur-laser');
  if(!g) return {present:false};
  var ps=[].map.call(g.querySelectorAll('.alur-laser-path'), function(p){
    var cs=getComputedStyle(p);
    return {cls:p.getAttribute('class'), w:cs.strokeWidth, stroke:cs.stroke,
            op:cs.opacity, dlen:(p.getAttribute('d')||'').length};
  });
  return {present:true, groupOpacity: g.getAttribute('opacity'),
          blend: getComputedStyle(g).mixBlendMode,
          layers: ps,
          head: (function(){var h=g.querySelector('.alur-laser-head');
            return h?{r:h.getAttribute('r'), cx:h.getAttribute('cx'), cy:h.getAttribute('cy'),
                     fill:getComputedStyle(h).fill}:null;})()};
})()"""

ev("document.querySelector('[data-tool=\"laser\"]').click()")
time.sleep(0.2)
ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()")

print('scene before', ev("(function(){return {nodes:Object.keys(window._state.spec.nodes).length, drawings:(window._state.spec.drawings||[]).length};})()"))

x0, y0 = ST['x'] + 420, ST['y'] + 300
ptr("pointerdown", x0, y0)
time.sleep(0.1)
print('at start', json.dumps(ev(SNAP)))
for k in range(1, 26):
    ptr("pointermove", x0 + k * 12, y0 + (k * k) * 0.22)
    time.sleep(0.012)
print('mid drag', json.dumps(ev(SNAP)))
ptr("pointerup", x0 + 300, y0 + 150, 0)
time.sleep(0.08)
print('just released', json.dumps(ev(SNAP)))
time.sleep(0.3)
print('fading', ev("(function(){var g=document.querySelector('.alur-laser');return g?g.getAttribute('opacity'):null;})()"))
time.sleep(0.8)
print('after fade', json.dumps(ev(SNAP)))
print('scene after', ev("(function(){return {nodes:Object.keys(window._state.spec.nodes).length, drawings:(window._state.spec.drawings||[]).length};})()"))

print('--- theme: dark core colour ---')
print(ev("(function(){var g=document.querySelector('.alur-laser');return g?'gone':'gone';})()"))
ev("document.querySelector('[data-tool=\"laser\"]').click()")
ptr("pointerdown", x0, y0)
for k in range(1, 10):
    ptr("pointermove", x0 + k * 10, y0 + k * 4)
    time.sleep(0.015)
print('dark core', ev("(function(){var p=document.querySelector('.laser-core');return p?getComputedStyle(p).stroke:null;})()"))
ptr("pointerup", x0 + 90, y0 + 36, 0)

ev("document.getElementById('themeToggle').click()")
time.sleep(0.5)
ev("document.querySelector('[data-tool=\"laser\"]').click()")
ptr("pointerdown", x0, y0 + 300)
for k in range(1, 10):
    ptr("pointermove", x0 + k * 10, y0 + 300 + k * 4)
    time.sleep(0.015)
print('light core', ev("(function(){var p=document.querySelector('.laser-core');return p?getComputedStyle(p).stroke:null;})()"))
print('light glow', ev("(function(){var p=document.querySelector('.laser-glow');return p?getComputedStyle(p).stroke:null;})()"))
ptr("pointerup", x0 + 90, y0 + 336, 0)
time.sleep(1.2)
print('cleaned', ev("(function(){return document.querySelectorAll('.alur-laser').length;})()"))
ev("document.getElementById('themeToggle').click()")
print('errs', ev("window.__errs"))
c.close(); proc.terminate()