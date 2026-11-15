import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9749
tmp=tempfile.mkdtemp(prefix="ppl")
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
def create(shape, dx, dy, ox=250, oy=280):
    ev("document.querySelector('[data-tool=\"" + shape + "\"]').click()")
    time.sleep(0.15)
    x0, y0 = ST['x'] + ox, ST['y'] + oy
    ptr("pointerdown", x0, y0)
    for k in range(1, 13):
        ptr("pointermove", x0 + dx * k / 12, y0 + dy * k / 12)
    ptr("pointerup", x0 + dx, y0 + dy, 0)
    time.sleep(0.5)
    return ev("(function(){var e=document.querySelectorAll('.alur-canvas-node');"
              "return e.length?e[e.length-1].getAttribute('data-node-id'):null;})()")

def select_at(x, y):
    ptr("pointerdown", x, y)
    ptr("pointerup", x, y, 0)
    time.sleep(0.4)

def panel_summary():
    return ev("""(function(){
      var host=document.getElementById('shapePanel');
      if(!host || host.hidden) return {hidden:true};
      return {title:((host.querySelector('.shape-head')||{}).textContent||'').replace(/\\s+/g,' ').trim(),
        rows: [].map.call(host.querySelectorAll('.prop-row'), function(r){
          return {l:((r.querySelector('.shape-label')||{}).textContent||'').trim()||null,
                  n:r.querySelectorAll('.prop-btn').length};}),
        selects: host.querySelectorAll('select').length,
        swatches: host.querySelectorAll('.swatch').length,
        ranges: host.querySelectorAll('input[type=range]').length,
        texts: host.querySelectorAll('input[type=text]').length};
    })()""")

print('== node ==')
nid = create('box', 200, 110)
select_at(ST['x'] + 350, ST['y'] + 335)
print(json.dumps(panel_summary(), indent=1))

print('== ellipse has no Edges ==')
create('circle', 200, 110, ox=520, oy=280)
select_at(ST['x'] + 620, ST['y'] + 335)
print(json.dumps(panel_summary(), indent=1))

print('== arrow (draw one) ==')
# select the box node, then draw an arrow from it
ev("document.querySelector('[data-tool=\"arrow\"]').click()")
time.sleep(0.2)
select_at(ST['x'] + 380, ST['y'] + 390)
select_at(ST['x'] + 700, ST['y'] + 390)
time.sleep(0.5)
print(json.dumps(panel_summary(), indent=1))

print('== text tool ==')
ev("document.querySelector('[data-tool=\"text\"]').click()")
time.sleep(0.4)
print(json.dumps(panel_summary(), indent=1))

print('== pen tool ==')
ev("document.querySelector('[data-tool=\"draw\"]').click()")
time.sleep(0.4)
print(json.dumps(panel_summary(), indent=1))

print('== theme light ==')
ev("document.getElementById('themeToggle').click()")
time.sleep(0.5)
print('light bg', ev("getComputedStyle(document.querySelector('.prop-btn')).backgroundColor"))
print('light pop', ev("(function(){var r=document.querySelectorAll('#shapePanel .prop-row');"
    "for(var k=0;k<r.length;k++){var b=r[k].querySelector('.color-open'); if(b){b.click(); break;}}"
    "var p=document.querySelector('.color-pop'); return p?getComputedStyle(p).backgroundColor:null;})()"))
ev("document.getElementById('themeToggle').click()")
time.sleep(0.3)
print('errs', ev("window.__errs"))
c.close(); proc.terminate()