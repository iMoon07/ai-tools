import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9755
tmp=tempfile.mkdtemp(prefix="ovp")
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

AUDIT = """(function(){
  var host=document.getElementById('shapePanel');
  if(!host || host.hidden) return {hidden:true};
  var hb=host.getBoundingClientRect();
  var over=[];
  host.querySelectorAll('.prop-btn, .swatch, .color-hex, .prop-grid').forEach(function(e){
    var r=e.getBoundingClientRect();
    if (r.width && (r.right > hb.right + 1 || r.left < hb.left - 1)) {
      over.push({cls:e.className, l:Math.round(r.left-hb.left), r:Math.round(r.right-hb.left)});
    }
  });
  var body=host.querySelector('.shape-body');
  var sw=document.documentElement.scrollWidth;
  var inner = body ? {clientW: body.clientWidth, scrollW: body.scrollWidth} : null;
  return {panelW:Math.round(hb.width), panelRight:Math.round(hb.right),
          viewport: window.innerWidth, docScrollW: sw,
          overflow: over.length, first: over.slice(0,3), inner: inner};
})()"""

for (w,h,label) in [(1400,900,'desktop'),(390,844,'mobile')]:
    cmd("Emulation.setDeviceMetricsOverride",width=w,height=h,deviceScaleFactor=1,mobile=(w<600))
    cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html?cb="+str(time.time())); time.sleep(3.2)
    ev("window.__errs=[];window.addEventListener('error',function(e){window.__errs.push(String(e.message));});")
    ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
    time.sleep(0.3)
    ev("""(function(){var S=window._state.spec;
      S.nodes['q1']={id:'q1',shape:'box',x:200,y:200,w:220,h:120,label:'Overflow check',color:'blue',fill:'#a5d8ff',sloppiness:'artist'};
      S.selected=null; S.selectedEdge=null; window._render();})()""")
    time.sleep(0.8)
    # real click on the node so the panel opens through the normal path
    ev("""(function(){var el=document.querySelector('.alur-canvas-node[data-node-id=\\"q1\\"]');
      if(!el) return 'no node';
      var r=el.getBoundingClientRect(); var s=document.getElementById('stage');
      var o={bubbles:true,cancelable:true,clientX:r.x+r.width/2,clientY:r.y+r.height/2,button:0,buttons:1,pointerId:1,pointerType:'mouse',isPrimary:true};
      s.dispatchEvent(new PointerEvent('pointerdown',o));
      s.dispatchEvent(new PointerEvent('pointerup',Object.assign({},o,{buttons:0})));})()""")
    time.sleep(0.7)
    if w < 600:
        ev("document.getElementById('shapePanel').hidden=false;")
        time.sleep(0.3)
    print(label, json.dumps(ev(AUDIT)))
    print(label, 'errs', ev("window.__errs"))
c.close(); proc.terminate()