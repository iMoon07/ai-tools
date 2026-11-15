import json, time, urllib.request, subprocess, tempfile, base64
import websocket
PORT=9763
tmp=tempfile.mkdtemp(prefix="fin")
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
cmd("Runtime.evaluate",expression="window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")

def load(w, h, mobile=False):
    cmd("Emulation.setDeviceMetricsOverride",width=w,height=h,deviceScaleFactor=1,mobile=mobile)
    cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html?cb="+str(time.time()))
    time.sleep(3.2)
    ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
    ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
    time.sleep(0.3)

def ptr(t, x, y, buttons=1):
    ev("(function(){var s=document.getElementById('stage');"
       "s.dispatchEvent(new PointerEvent(" + json.dumps(t) + ",{bubbles:true,cancelable:true,"
       "clientX:%d,clientY:%d,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()"
       % (x, y, buttons))

def drag(x0, y0, x1, y1, steps=10):
    ptr("pointerdown", x0, y0)
    for k in range(1, steps + 1):
        ptr("pointermove", x0 + (x1 - x0) * k / steps, y0 + (y1 - y0) * k / steps)
    ptr("pointerup", x1, y1, 0)
    time.sleep(0.45)

def tap(x, y):
    ptr("pointerdown", x, y); ptr("pointerup", x, y, 0); time.sleep(0.4)

def report(label):
    r = ev("""(function(){
      var p=document.getElementById('shapePanel');
      var b=p.querySelector('.shape-body');
      var bad=[];
      document.querySelectorAll('#stage *').forEach(function(e){});
      return {errs: window.__errs.slice(),
              panel: p.hidden? null : {w:Math.round(p.getBoundingClientRect().width),
                     scrollW:b.scrollWidth, clientW:b.clientWidth},
              docW: document.documentElement.scrollWidth,
              view: window.innerWidth,
              nodes: document.querySelectorAll('.alur-canvas-node').length,
              rough: document.querySelectorAll('.alur-node-rough').length,
              laser: document.querySelectorAll('.alur-laser').length,
              sticky: document.querySelectorAll('.alur-sticky-node').length};
    })()""")
    print(label, json.dumps(r))
    return r

# ---------- DESKTOP ----------
load(1400, 900)
ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y};})()")
report('desktop initial')

ev("document.querySelector('[data-tool=\"box\"]').click()")
drag(ST['x'] + 200, ST['y'] + 200, ST['x'] + 380, ST['y'] + 300)
tap(ST['x'] + 290, ST['y'] + 250)
report('desktop node selected')

# roughness + colour through the panel
ev("(function(){var ss=document.querySelectorAll('#shapePanel .pp-sec');"
   "for(var i=0;i<ss.length;i++){var cap=ss[i].querySelector('.pp-cap');"
   "if(cap&&cap.textContent.trim().indexOf('Roughness')===0){ss[i].querySelectorAll('.pp-seg button')[2].click();}}})()")
time.sleep(0.5)
print('cartoonist rough paths', ev("(function(){var id=window._state.spec.selected;"
  "var e=document.querySelector('.alur-canvas-node[data-node-id=\"'+id+'\"]');return e?e.querySelectorAll('.alur-node-rough').length:-1;})()"))

ev("(function(){var p=document.querySelector('.pp-custom'); if(p) p.click();})()")
time.sleep(0.3)
print('picker', ev("(function(){var p=document.querySelector('.color-pop');"
  "return p?{pal:p.querySelectorAll('.pal .swatch').length,shades:p.querySelectorAll('.shades .swatch').length}:null;})()"))
ev("var x=document.querySelector('.color-pop'); if(x) x.querySelectorAll('.pal .swatch')[6].click();")
time.sleep(0.4)
print('picked colour', ev("(function(){var n=window._state.spec.nodes[window._state.spec.selected];return n.color;})()"))

# sticky
ev("document.querySelector('[data-tool=\"sticky\"]').click()")
drag(ST['x'] + 600, ST['y'] + 200, ST['x'] + 760, ST['y'] + 360)
report('desktop sticky')

# laser
ev("document.querySelector('[data-tool=\"laser\"]').click()")
drag(ST['x'] + 300, ST['y'] + 500, ST['x'] + 700, ST['y'] + 600, 14)
print('laser layers', ev("document.querySelectorAll('.alur-laser-path').length"))
time.sleep(0.9)
report('desktop after laser fade')

# theme switch while editor in use (beam still alive)
ev("document.querySelector('[data-tool=\"laser\"]').click()")
ptr("pointerdown", ST['x'] + 320, ST['y'] + 520)
for k in range(1, 8):
    ptr("pointermove", ST['x'] + 320 + k * 12, ST['y'] + 520 + k * 3)
    time.sleep(0.02)
print('dark core live', ev("(function(){var p=document.querySelector('.laser-core');return p?getComputedStyle(p).stroke:'none';})()"))
ev("document.getElementById('themeToggle').click()")
time.sleep(0.25)
print('light core live', ev("(function(){var p=document.querySelector('.laser-core');return p?getComputedStyle(p).stroke:'none';})()"))
ptr("pointerup", ST['x'] + 404, ST['y'] + 541, 0)
time.sleep(0.9)
ev("document.getElementById('themeToggle').click()")
time.sleep(0.5)
print('light core', ev("(function(){var p=document.querySelector('.laser-core');return p?getComputedStyle(p).stroke:'no beam';})()"))
time.sleep(0.4)

# zoom + pan + selection still work
ev("window._editor.tool='select'")
before = ev("(function(){return document.querySelector('#stage svg').getAttribute('viewBox');})()")
ev("document.getElementById('zoomIn').click()")
time.sleep(0.5)
after = ev("(function(){return document.querySelector('#stage svg').getAttribute('viewBox');})()")
print('zoom changed', before != after)

# ---------- TABLET ----------
load(820, 1180, mobile=True)
report('tablet')
ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y};})()")
ev("document.querySelector('[data-tool=\"sticky\"]').click()")
drag(ST['x'] + 200, ST['y'] + 300, ST['x'] + 340, ST['y'] + 440)
tap(ST['x'] + 270, ST['y'] + 370)
ev("var t=document.getElementById('inspectorToggle'); if(t && document.getElementById('shapePanel').hidden) t.click();")
time.sleep(0.6)
report('tablet sticky panel')

# ---------- MOBILE ----------
load(390, 844, mobile=True)
report('mobile')
ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y};})()")
ev("document.querySelector('[data-tool=\"box\"]').click()")
drag(ST['x'] + 80, ST['y'] + 200, ST['x'] + 240, ST['y'] + 300)
tap(ST['x'] + 160, ST['y'] + 250)
ev("var t=document.getElementById('inspectorToggle'); if(t && document.getElementById('shapePanel').hidden) t.click();")
time.sleep(0.6)
report('mobile panel')
print('touch sizes', ev("""(function(){
  var p=document.getElementById('shapePanel');
  if(!p || p.hidden) return 'hidden';
  var seg=p.querySelector('.pp-seg button'), dot=p.querySelector('.pp-dot'), act=p.querySelector('.pp-acts button');
  return {seg: seg?Math.round(seg.getBoundingClientRect().height):0,
          dot: dot?Math.round(dot.getBoundingClientRect().width):0,
          act: act?Math.round(act.getBoundingClientRect().height):0};
})()"""))

# ---------- READER ----------
cmd("Emulation.setDeviceMetricsOverride",width=1200,height=900,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/read.html?cb="+str(time.time()))
time.sleep(3.0)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
print('reader', json.dumps(ev("""(function(){
  var spec={module:'canvas',title:'r',nodes:{
    a:{id:'a',shape:'sticky',x:40,y:40,w:180,h:180,label:'hello world this is a note',fill:'#ffec99'},
    b:{id:'b',shape:'circle',x:260,y:60,w:220,h:110,label:'oval',color:'#1971c2',fill:'#a5d8ff',sloppiness:'cartoonist'},
    c:{id:'c',shape:'diamond',x:260,y:220,w:200,h:120,label:'d',color:'#e03131',fill:'#ffc9c9',sloppiness:'artist'}},
    edges:[{from:'a',to:'b'},{from:'b',to:'c',elbow:true}],selected:null,selectedEdge:null,zoom:1,panX:0,panY:0};
  var d=document.createElement('div'); d.className='alur draw';
  d.setAttribute('data-spec', JSON.stringify(spec)); document.body.appendChild(d);
  window.Alur.mount(d);
  return {nodes:d.querySelectorAll('.alur-canvas-node').length,
          sticky:d.querySelectorAll('.alur-sticky-node').length,
          rough:d.querySelectorAll('.alur-node-rough').length,
          edges:d.querySelectorAll('.alur-canvas-edge').length};
})()""")))
print('reader errs', ev("window.__errs"))
c.close(); proc.terminate()