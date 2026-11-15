import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9741
tmp=tempfile.mkdtemp(prefix="rpe")
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

def ptr(t, x, y, extra=""):
    ev("""(function(){var s=document.getElementById('stage');
      s.dispatchEvent(new PointerEvent(%s,{bubbles:true,cancelable:true,clientX:%d,clientY:%d,button:0,buttons:%s,pointerId:1,pointerType:'mouse',isPrimary:true}));})()"""
       % (json.dumps(t), x, y, "1" if t != "pointerup" else "0"))

st = ev("""(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()""")
print('stage', st)

# draw an ellipse (wide drag with the circle tool)
ev("""(function(){document.querySelector('[data-tool="circle"]').click();})()""")
time.sleep(0.2)
x0, y0 = st['x'] + 260, st['y'] + 300
ptr("pointerdown", x0, y0)
for k in range(1, 13):
    ptr("pointermove", x0 + k * 22, y0 + k * 7.5)
ptr("pointerup", x0 + 264, y0 + 90)
time.sleep(0.6)

info = ev("""(function(){
  var els=document.querySelectorAll('.alur-canvas-node');
  return Array.prototype.map.call(els,function(el){
    var ell=el.querySelector('ellipse');
    var box=el.querySelector('.alur-node-box');
    var rough=el.querySelectorAll('.alur-node-rough');
    return {id:el.getAttribute('data-node-id'),
      tag: box?box.tagName:null,
      rx: ell?+ell.getAttribute('rx'):null, ry: ell?+ell.getAttribute('ry'):null,
      cx: ell?+ell.getAttribute('cx'):null, cy: ell?+ell.getAttribute('cy'):null,
      rough: rough.length,
      roughD: rough.length?(rough[0].getAttribute('d')||'').slice(0,40):null,
      nodeW: null};
  });
})()""")
print('nodes', json.dumps(info, indent=1))
nid = info[-1]['id'] if info else None

def node_state(nid):
    return ev("""(function(){var n=window._state.spec.nodes[%s]; if(!n) return null;
      return {id:n.id,shape:n.shape,w:Math.round(n.w),h:Math.round(n.h),sloppiness:n.sloppiness};})()""" % json.dumps(nid))

print('spec', node_state(nid))

# set sloppiness via the panel select
def set_slop(v):
    return ev("""(function(){
      var host=document.getElementById('shapePanel');
      var sels=host?host.querySelectorAll('select'):[];
      for (var k=0;k<sels.length;k++){
        var row=sels[k].closest('.shape-row')||sels[k].parentNode;
        if ((row.textContent||'').indexOf('Sloppiness')>=0){ sels[k].value=%s;
          sels[k].dispatchEvent(new Event('change',{bubbles:true})); return sels[k].value; }
      }
      return null;})()""" % json.dumps(v))

# select the new node so the shape panel opens
ev("""(function(){var el=document.querySelector('.alur-canvas-node[data-node-id=\"%s\"]');
  var r=el.getBoundingClientRect(); var s=document.getElementById('stage');
  s.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,clientX:%d,clientY:%d,button:0,buttons:1,pointerId:1,pointerType:'mouse',isPrimary:true}));
  s.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,cancelable:true,clientX:%d,clientY:%d,button:0,buttons:0,pointerId:1,pointerType:'mouse',isPrimary:true}));})()""" % (nid, st['x']+400, st['y']+360, st['x']+400, st['y']+360))
time.sleep(0.5)
print('panel open', ev("!!document.getElementById('shapePanel') && !document.getElementById('shapePanel').hidden"))
print('slop set ->', set_slop('cartoonist'))
time.sleep(0.6)
print('after', json.dumps(ev("""(function(){
  var el=document.querySelector('.alur-canvas-node[data-node-id="%s"]');
  var r=el.querySelectorAll('.alur-node-rough');
  return {spec: window._state.spec.nodes[%s].sloppiness,
    rough: r.length,
    d0: r.length?(r[0].getAttribute('d')||'').slice(0,60):null,
    d1: r.length>1?(r[1].getAttribute('d')||'').slice(0,40):null,
    boxStroke: (el.querySelector('.alur-node-box')||{}).getAttribute?el.querySelector('.alur-node-box').getAttribute('stroke'):null,
    fill: (el.querySelector('.alur-node-box')||{}).getAttribute?el.querySelector('.alur-node-box').getAttribute('fill'):null};})()""" % (nid, nid))))

print('DBG', ev("""(function(){
  var n=window._state.spec.nodes[%s];
  var k=window.AlurKit;
  return {hasKit: !!k, hasNodeRough: !!(k&&k.nodeRough),
    amp: k&&k.roughAmp? k.roughAmp(n.sloppiness):'no fn',
    r: k&&k.nodeRough? (function(){var x=k.nodeRough(n); return x?{d:x.d.slice(0,40),d2:!!x.d2}:null;})():'no fn',
    slop: n.sloppiness, shape: n.shape};})()""" % json.dumps(nid)))

# persistence across deselect / reselect / rerender
ev("""(function(){document.body.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,clientX:5,clientY:5,button:0,buttons:1,pointerId:1,pointerType:'mouse'}));})()""")
time.sleep(0.4)
before = ev("""(function(){var el=document.querySelector('.alur-canvas-node[data-node-id="%s"]');
  var r=el.querySelectorAll('.alur-node-rough'); return (r[0]||{}).getAttribute?r[0].getAttribute('d').slice(0,50):null;})()""" % nid)
ev("window._render()")
time.sleep(0.6)
after = ev("""(function(){var el=document.querySelector('.alur-canvas-node[data-node-id="%s"]');
  var r=el.querySelectorAll('.alur-node-rough'); return (r[0]||{}).getAttribute?r[0].getAttribute('d').slice(0,50):null;})()""" % nid)
print('stable across rerender:', before == after)

# resize the ellipse wide -> should get longer, not stay round
print('errs', ev("window.__errs"))
c.close(); proc.terminate()