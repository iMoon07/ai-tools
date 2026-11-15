import json,time,urllib.request,subprocess,tempfile
import websocket
PORT=9796
tmp=tempfile.mkdtemp(prefix="sel")
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
    i[0]+=1;c.send(json.dumps({"id":i[0],"method":m,"params":p}))
    while True:
        r=json.loads(c.recv())
        if r.get("id")==i[0]: return r.get("result",{})
def ev(e):
    r=cmd("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
cmd("Page.enable");cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html?cb="+str(time.time()))
time.sleep(3.4)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
SPEC={"module":"canvas","nodes":{
 "a":{"x":200,"y":200,"w":200,"h":110,"text":"API","shape":"box"},
 "b":{"x":520,"y":200,"w":200,"h":110,"text":"DB","shape":"box"}},
 "edges":[{"from":"a","to":"b","arrowEnd":True}]}
ev("""(function(){var box=document.getElementById('drawCode');
 box.value='```draw\\n'+JSON.stringify(%s,null,2)+'\\n```';
 document.getElementById('applyCode').click();})()""" % json.dumps(SPEC))
time.sleep(1.2)
def ptr(t,x,y,b=1):
    ev("""(function(){var s=document.querySelector('.alur-canvas-node')||document.getElementById('stage');
      s.dispatchEvent(new PointerEvent(%s,{bubbles:true,cancelable:true,clientX:%f,clientY:%f,button:0,buttons:%d,pointerId:1,pointerType:'mouse',isPrimary:true}));})()""" % (json.dumps(t),x,y,b))
def tap(x,y):
    ptr("pointerdown",x,y); ptr("pointerup",x,y,0); time.sleep(0.5)
def dump(label):
    print(label, json.dumps(ev("""(function(){
      var o=document.querySelector('.alur-selection-outline');
      var hs=[].slice.call(document.querySelectorAll('.alur-handle'));
      var rt=document.querySelector('.alur-rotate-handle');
      var cs=function(e){var c=getComputedStyle(e);return {stroke:c.stroke,fill:c.fill,w:c.strokeWidth};};
      return {outline: o?{x:+o.getAttribute('x'),y:+o.getAttribute('y'),w:+o.getAttribute('width'),h:+o.getAttribute('height'),style:cs(o)}:null,
              handles:hs.map(function(h){return h.getAttribute('data-handle')+'@'+Math.round(+h.getAttribute('x'))+','+Math.round(+h.getAttribute('y'))+' '+h.getAttribute('width')+'x'+h.getAttribute('height');}),
              handleStyle:hs.length?cs(hs[0]):null,
              rotate: rt?{cx:+rt.getAttribute('cx'),cy:+rt.getAttribute('cy'),r:+rt.getAttribute('r'),style:cs(rt)}:null};})()""")))
tap(300,255)
dump("single:")
print("zoom:", ev("document.getElementById('zoomVal').textContent"))
# zoom in 2x and re-measure (handle must stay 8 screen px)
ev("document.getElementById('zoomIn').click(); document.getElementById('zoomIn').click();")
time.sleep(0.6)
print("zoom now:", ev("document.getElementById('zoomVal').textContent"))
dump("zoomed:")
# multi-select: shift-click second node
ptr("pointerdown",620,255); ptr("pointerup",620,255,0)
ev("""(function(){var s=document.querySelector('.alur-canvas-node[data-node-id=\\"b\\"]');
  s.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,clientX:620,clientY:255,button:0,buttons:1,pointerId:1,pointerType:'mouse',shiftKey:true}));
  s.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,cancelable:true,clientX:620,clientY:255,button:0,buttons:0,pointerId:1,pointerType:'mouse',shiftKey:true}));})()""")
time.sleep(0.6)
dump("multi:")
print("errs:", ev("window.__errs"))
proc.terminate()
