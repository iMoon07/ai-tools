import json, time, urllib.request, subprocess, tempfile, sys
import websocket
W = int(sys.argv[1]) if len(sys.argv)>1 else 1400
PORT=9637
tmp=tempfile.mkdtemp(prefix="tp4")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=%d,900"%W,"about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
    r=cmd("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)["result"]
    if r.get("subtype")=="error": return {"__err":r.get("description")}
    return r.get("value")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=W,height=900,deviceScaleFactor=1,mobile=(W<500))
if W<500: cmd("Emulation.setTouchEmulationEnabled",enabled=True,maxTouchPoints=5)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("document.querySelectorAll('.dock.is-open [data-close]').forEach(function(b){b.click();});")
time.sleep(0.3)
ev("""(function(){
  var st=document.getElementById('stage'); var r=st.getBoundingClientRect();
  var x=r.left+r.width/2, y=r.top+r.height/2;
  st.dispatchEvent(new PointerEvent('pointerdown',{clientX:x,clientY:y,button:0,buttons:1,pointerId:1,pointerType:'mouse',bubbles:true}));
  st.dispatchEvent(new PointerEvent('pointerup',{clientX:x,clientY:y,button:0,buttons:0,pointerId:1,pointerType:'mouse',bubbles:true}));
})();""")
time.sleep(0.5)
ev("""(function(){
  var a=document.getElementById('inlineText');
  if(a){a.value='Hi'; a.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));}
})();""")
time.sleep(0.5)
ev("""(function(){
  var S=window._state; var id=Object.keys(S.spec.nodes)[0]; S.spec.selected=id; window._syncShapePanel();
})();""")
time.sleep(0.3)
out = ev("""(function(){
  var b=document.getElementById('shapePanelBody');
  var p=document.getElementById('shapePanel');
  var btns=Array.from(b.querySelectorAll('button')).map(function(x){return {t:(x.textContent||'').trim(),cls:x.className};});
  var r=p.getBoundingClientRect();
  return {hidden:p.hidden, rect:{x:r.x,y:r.y,w:r.width,h:r.height}, vis:getComputedStyle(p).display, btns:btns};
})()""")
print(json.dumps(out, indent=1))
c.close(); proc.terminate()
