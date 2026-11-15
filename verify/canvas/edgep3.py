import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9751
tmp=tempfile.mkdtemp(prefix="ppe")
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

ev("""(function(){
  var S=window._state.spec;
  S.nodes['p1']={id:'p1',shape:'box',x:300,y:250,w:170,h:80,label:'API',color:'blue'};
  S.nodes['p2']={id:'p2',shape:'box',x:700,y:250,w:170,h:80,label:'DB',color:'green'};
  S.edges=[{from:'p1',to:'p2',label:'reads',color:'cyan',width:2}];
  S.selected=null; S.selectedEdge=null;
  window._render();
})()""")
time.sleep(0.9)

# click the middle of the cable
info = ev("""(function(){
  var p=document.querySelector('.alur-canvas-edge');
  if(!p) return null;
  var pt=p.getPointAtLength(p.getTotalLength()/2);
  var m=p.getScreenCTM(); var r=document.getElementById('stage').getBoundingClientRect();
  return {x: pt.x*m.a + pt.y*m.c + m.e, y: pt.x*m.b + pt.y*m.d + m.f};
})()""")
print('mid', info)
if info:
    ev("(function(){var p=document.querySelector('.alur-canvas-edge');"
       "var o={bubbles:true,cancelable:true,clientX:%d,clientY:%d,button:0,buttons:1,pointerId:1,pointerType:'mouse',isPrimary:true};"
       "p.dispatchEvent(new PointerEvent('pointerdown',o));"
       "p.dispatchEvent(new PointerEvent('pointerup',Object.assign({},o,{buttons:0})));})()"
       % (STX := info['x'], STY := info['y']))
    time.sleep(0.5)

print(json.dumps(ev("""(function(){
  var host=document.getElementById('shapePanel');
  if(!host || host.hidden) return {hidden:true};
  return {title:((host.querySelector('.shape-head')||{}).textContent||'').replace(/\\s+/g,' ').trim(),
    rows: [].map.call(host.querySelectorAll('.prop-row'), function(r){
      return {l:((r.querySelector('.shape-label')||{}).textContent||'').trim()||null,
              n:r.querySelectorAll('.prop-btn').length,
              on:r.querySelectorAll('.prop-btn.is-on').length};}),
    selects: host.querySelectorAll('select').length,
    swatches: host.querySelectorAll('.swatch').length,
    labelField: !!host.querySelector('.color-hex')};
})()"""), indent=1))

# toggle elbow, check the path becomes orthogonal
ev("(function(){var rs=document.querySelectorAll('#shapePanel .prop-row');"
   "for(var k=0;k<rs.length;k++){var l=rs[k].querySelector('.shape-label');"
   "if(l&&l.textContent.trim()==='Arrow head'){ var b=rs[k].querySelectorAll('.prop-btn')[1]; b.click(); return; } }})()")
time.sleep(0.5)
print('arrowType', ev("(function(){return window._state.spec.edges[0].arrowType;})()"))
print('elbow d', ev("(function(){var p=document.querySelector('.alur-canvas-edge');return (p.getAttribute('d')||'').slice(0,90);})()"))

ev("(function(){var rs=document.querySelectorAll('#shapePanel .prop-row');"
   "for(var k=0;k<rs.length;k++){var l=rs[k].querySelector('.shape-label');"
   "if(l&&l.textContent.trim()!=='Arrow head') continue;"
   "var g=rs[k].parentNode.querySelectorAll('.prop-row');"
   "for(var j=0;j<g.length;j++){var b=g[j].querySelectorAll('.prop-btn');"
   "for(var m=0;m<b.length;m++){ if(b[m].title==='Elbow path'){ b[m].click(); return; } } } }})()")
time.sleep(0.6)
print('elbow?', ev("(function(){return window._state.spec.edges[0].elbow;})()"))
print('elbow d', ev("(function(){var p=document.querySelector('.alur-canvas-edge');return (p.getAttribute('d')||'').slice(0,90);})()"))
print('errs', ev("window.__errs"))
c.close(); proc.terminate()