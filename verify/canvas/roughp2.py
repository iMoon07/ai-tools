import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9743
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

ST = ev("(function(){var r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()")

def ptr(t, x, y, buttons=1):
    ev("(function(){var s=document.getElementById('stage');"
       "s.dispatchEvent(new PointerEvent(" + json.dumps(t) + ",{bubbles:true,cancelable:true,"
       "clientX:%d,clientY:%d,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()"
       % (x, y, buttons))

def create(shape, dx, dy):
    ev("document.querySelector('[data-tool=\"" + shape + "\"]').click()")
    time.sleep(0.15)
    x0, y0 = ST['x'] + 250, ST['y'] + 280
    ptr("pointerdown", x0, y0)
    for k in range(1, 13):
        ptr("pointermove", x0 + dx * k / 12, y0 + dy * k / 12)
    ptr("pointerup", x0 + dx, y0 + dy, 0)
    time.sleep(0.5)
    return ev("(function(){var e=document.querySelectorAll('.alur-canvas-node');"
              "return e.length?e[e.length-1].getAttribute('data-node-id'):null;})()")

def probe(nid):
    return ev("""(function(){
      var el=document.querySelector('.alur-canvas-node[data-node-id="NID"]');
      if(!el) return null;
      var box=el.querySelector('.alur-node-box');
      var r=el.querySelectorAll('.alur-node-rough');
      var ell=el.querySelector('ellipse');
      return {
        tag: box?box.tagName:null,
        rx: ell?+ell.getAttribute('rx'):null, ry: ell?+ell.getAttribute('ry'):null,
        boxStroke: box?box.getAttribute('stroke'):null,
        fill: box?box.getAttribute('fill'):null,
        rough: r.length,
        d0: r.length?(r[0].getAttribute('d')||'').slice(0,34):null,
        d1: r.length>1?(r[1].getAttribute('d')||'').slice(0,30):null,
        op: el.getAttribute('opacity')
      };} )()""".replace("NID", nid))

nid = create('circle', 264, 88)
print('created', nid, 'spec', ev("JSON.stringify((function(){var n=window._state.spec.nodes[%s];return {w:Math.round(n.w),h:Math.round(n.h),shape:n.shape};})())" % json.dumps(nid)))
print('before', json.dumps(probe(nid)))

def set_slop(v):
    return ev("""(function(){
      var sels=document.querySelectorAll('#shapePanel select, .shape-group select');
      for (var k=0;k<sels.length;k++){
        var lab=sels[k].closest('label');
        if (lab && (lab.textContent||'').trim().indexOf('Sloppiness')===0){
          sels[k].value=%s;
          sels[k].dispatchEvent(new Event('change',{bubbles:true}));
          return sels[k].value; }
      }
      return 'not found';})()""" % json.dumps(v))

ev("(function(){var el=document.querySelector('.alur-canvas-node[data-node-id=\"%s\"]');"
   "var r=el.getBoundingClientRect();"
   "document.getElementById('stage').dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,clientX:%d,clientY:%d,button:0,buttons:1,pointerId:1,pointerType:'mouse',isPrimary:true}));"
   "document.getElementById('stage').dispatchEvent(new PointerEvent('pointerup',{bubbles:true,cancelable:true,clientX:%d,clientY:%d,button:0,buttons:0,pointerId:1,pointerType:'mouse',isPrimary:true}));})()"
   % (nid, r_x := ST['x'] + 382, r_y := ST['y'] + 324, r_x, r_y))
time.sleep(0.4)
print('panel?', ev("!!document.getElementById('shapePanel')"))
print('sels', ev("""(function(){var out=[];document.querySelectorAll('select').forEach(function(s){
  out.push({label:(s.closest('label')||s.parentNode).textContent.trim().slice(0,40),
            val:s.value, opts:Array.prototype.map.call(s.options,function(o){return o.value;}).join('|')});});
  return JSON.stringify(out);})()"""))
print('slop ->', repr(set_slop('cartoonist')))
print('spec slop now', ev("(function(){var n=window._state.spec.nodes[%s];return n.sloppiness;})()" % json.dumps(nid)))
time.sleep(0.7)
print('after ', json.dumps(probe(nid)))

# stable across a deselect + rerender
ev("document.getElementById('stage').dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,clientX:4,clientY:4,button:0,buttons:1,pointerId:1,pointerType:'mouse',isPrimary:true}));")
time.sleep(0.4)
d1 = probe(nid)['d0']
ev("window._render()")
time.sleep(0.7)
d2 = probe(nid)['d0']
print('stable', d1 == d2)

# artist / architect
for v in ('artist', 'architect'):
    ev("""(function(){
      var sels=document.querySelectorAll('#shapePanel select, .shape-group select');
      for (var k=0;k<sels.length;k++){ var lab=sels[k].closest('label');
        if (lab && (lab.textContent||'').trim().indexOf('Sloppiness')===0){
          sels[k].value=%s; sels[k].dispatchEvent(new Event('change',{bubbles:true})); return; } }})()""" % json.dumps(v))
    time.sleep(0.6)
    print(v, json.dumps(probe(nid)))

# visual: three copies of the ellipse, one per sloppiness
ev("""(function(){
  var st=window._state; var base=st.spec.nodes[%s];
  ['architect','artist','cartoonist'].forEach(function(v,k){
    st.spec.nodes['s'+k]={id:'s'+k,shape:'circle',x:120+k*300,y:120,w:264,h:88,
      label:v,color:'#58a6ff',fill:'#a5d8ff',sloppiness:v,fillStyle:'solid'};
  });
  st.spec.nodes['d0']={id:'d0',shape:'diamond',x:120,y:300,w:264,h:150,label:'diamond',
    color:'#d29922',fill:'#ffec99',sloppiness:'cartoonist',fillStyle:'hachure'};
  st.spec.nodes['b0']={id:'b0',shape:'box',x:420,y:300,w:264,h:110,label:'box',
    color:'#3fb950',fill:'#b2f2bb',sloppiness:'artist',fillStyle:'solid'};
  window._render();
})()""" % json.dumps(nid))
time.sleep(1.0)
r=ev("(function(){var s=document.getElementById('stage').getBoundingClientRect();return {x:Math.round(s.x),y:Math.round(s.y),w:Math.round(s.width),h:Math.round(s.height)};})()")
data=cmd("Page.captureScreenshot",format="png",clip={"x":r['x'],"y":r['y'],"width":r['w'],"height":r['h'],"scale":1}).get("data")
import base64
open('/tmp/alur-probes/rough1.png','wb').write(base64.b64decode(data))
print('shot', r)

# resize ellipse via corner handle: should stretch ry too
print('errs', ev("window.__errs"))
c.close(); proc.terminate()