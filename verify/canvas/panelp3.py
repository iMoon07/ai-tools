import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9757
tmp=tempfile.mkdtemp(prefix="pn3")
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
    ptr("pointerdown", x, y); ptr("pointerup", x, y, 0); time.sleep(0.45)

SUMMARY = """(function(){
  var host=document.getElementById('shapePanel');
  if(!host || host.hidden) return {hidden:true};
  var secs=[].map.call(host.querySelectorAll('.pp-sec'), function(s){
    var cap=s.querySelector('.pp-cap');
    var segs=[].map.call(s.querySelectorAll('.pp-seg'), function(g){
      return {n:g.querySelectorAll('button').length,
              on:g.querySelectorAll('button[aria-pressed="true"]').length};
    });
    return {cap: cap? cap.textContent.replace(/\\s+/g,' ').trim() : null,
            dots: s.querySelectorAll('.pp-dot').length,
            segs: segs,
            slider: s.querySelectorAll('.pp-range').length,
            acts: s.querySelectorAll('.pp-acts button').length};
  });
  var hb=host.getBoundingClientRect();
  var body=host.querySelector('.shape-body');
  return {title:((host.querySelector('.shape-head b')||{}).textContent||'').trim(),
          w:Math.round(hb.width), h:Math.round(hb.height),
          clientW: body.clientWidth, scrollW: body.scrollWidth,
          secs: secs};
})()"""

print('== node ==')
nid = create('box', 200, 110)
select_at(ST['x'] + 350, ST['y'] + 335)
print(json.dumps(ev(SUMMARY), indent=1))

print('== ellipse ==')
create('circle', 200, 110, ox=520, oy=280)
select_at(ST['x'] + 620, ST['y'] + 335)
print(json.dumps(ev(SUMMARY), indent=1))

print('== style checks ==')
print(json.dumps(ev("""(function(){
  var p=document.getElementById('shapePanel');
  var cs=getComputedStyle(p);
  var seg=p.querySelector('.pp-seg');
  var on=seg?seg.querySelector('button[aria-pressed="true"]'):null;
  var r=p.querySelector('.pp-range');
  return {radius:cs.borderRadius, width:cs.width, bg:cs.backgroundColor,
          segBg: seg?getComputedStyle(seg).backgroundColor:null,
          segRadius: seg?getComputedStyle(seg).borderRadius:null,
          onBg: on?getComputedStyle(on).backgroundColor:null,
          onRadius: on?getComputedStyle(on).borderRadius:null,
          dot: p.querySelector('.pp-dot')?{
            w:getComputedStyle(p.querySelector('.pp-dot')).width,
            r:getComputedStyle(p.querySelector('.pp-dot')).borderRadius}:null,
          rangeFill: r?r.style.getPropertyValue('--pp-fill'):null};
})()"""), indent=1))

print('== interactions ==')
# click the "Bold" stroke width (3rd segment of first seg = Width)
print('width bold', ev("(function(){var s=document.querySelectorAll('#shapePanel .pp-sec')[0];"
  "var g=s.querySelector('.pp-seg'); var b=g.querySelectorAll('button')[2]; b.click(); return b.title;})()"))
time.sleep(0.4)
print('keys', ev("(function(){return Object.keys(window._state.spec.nodes).join(',');})()"))
print('sel', ev("(function(){return JSON.stringify(window._state.spec.selected);})()"))
print('n4', ev("(function(){return JSON.stringify(window._state.spec.nodes['n4']);})()"))
# roughness artist
print('rough', ev("(function(){var ss=document.querySelectorAll('#shapePanel .pp-sec');"
  "for(var i=0;i<ss.length;i++){var cap=ss[i].querySelector('.pp-cap');"
  "if(cap&&cap.textContent.trim().indexOf('Roughness')===0){var b=ss[i].querySelectorAll('.pp-seg button')[1];b.click();return b.title;}}return 'no';})()"))
time.sleep(0.5)
print('slop', ev("(function(){var n=window._state.spec.nodes[window._state.spec.selected];return n.sloppiness;})()"))
print('rough paths', ev("(function(){var e=document.querySelector('.alur-canvas-node[data-node-id=\"%s\"]');return e.querySelectorAll('.alur-node-rough').length;})()" % nid))
# opacity slider
print('opacity', ev("(function(){var ss=document.querySelectorAll('#shapePanel .pp-sec');"
  "for(var i=0;i<ss.length;i++){var cap=ss[i].querySelector('.pp-cap');"
  "if(cap&&cap.textContent.trim().indexOf('Opacity')===0){var r=ss[i].querySelector('.pp-range');"
  "r.value=45; r.dispatchEvent(new Event('input',{bubbles:true}));"
  "return {fill:r.style.getPropertyValue('--pp-fill'), val:cap.querySelector('.pp-val').textContent};}}return 'no';})()"))
time.sleep(0.4)
print('node opacity', ev("(function(){var n=window._state.spec.nodes[window._state.spec.selected];return n.opacity;})()"))

print('== light mode ==')
ev("document.getElementById('themeToggle').click()")
time.sleep(0.6)
print(json.dumps(ev("""(function(){
  var p=document.getElementById('shapePanel'); var cs=getComputedStyle(p);
  var on=p.querySelector('.pp-seg button[aria-pressed="true"]');
  return {panelBg:cs.backgroundColor, text:getComputedStyle(p).color,
          onBg: on?getComputedStyle(on).backgroundColor:null,
          hexBg: getComputedStyle(p.querySelector('.pp-hex')).backgroundColor};
})()""")))
ev("document.getElementById('themeToggle').click()")
time.sleep(0.3)
print('dbg', ev("""(function(){
  var n=window._state.spec.nodes[window._state.spec.selected];
  var out={id:n.id, shape:n.shape, slop:n.sloppiness, w:n.w, h:n.h,
           hasRough: !!(window.rough && window.rough.generator),
           nodeRough: null};
  try { var r=AlurKit.nodeRough(n); out.nodeRough = r? r.strokes.length : null; } catch(e){ out.err=String(e); }
  var el=document.querySelector('.alur-canvas-node[data-node-id="'+n.id+'"]');
  out.dom = el? el.querySelectorAll('.alur-node-rough').length : 'no el';
  return out;})()"""))
print('errs', ev("window.__errs"))
c.close(); proc.terminate()