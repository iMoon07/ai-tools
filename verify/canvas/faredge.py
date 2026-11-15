import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9883
tmp=tempfile.mkdtemp(prefix="fe")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=1600,1000","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
    if r.get("subtype")=="error": print("JS ERROR:",r.get("description"))
    return r.get("value")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.2)

spec = {
 "module":"canvas","title":"far","width":1600,"height":900,
 "nodes":{"a":{"x":100,"y":200,"w":160,"h":60,"label":"A"}},
 "edges":[
   {"from":"a","points":[[180,230],[2600,1400]],"arrowEnd":True},
   {"from":"a","points":[[180,230],[300,1800]],"arrowEnd":True}
 ]
}
ev("""
(function(){
  if(!window.__origSet){ window.__origSet = localStorage.setItem.bind(localStorage);
    localStorage.setItem = function(k,v){ if(k==='ruang.scene.v1') return; return window.__origSet(k,v); }; }
  window.__origSet('ruang.scene.v1', %s);
  return 'seeded';
})()""" % json.dumps(json.dumps(spec)))
cmd("Page.reload"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")
print("mask:", ev("""(function(){var m=document.querySelector('#stage svg mask');
 if(!m) return null;
 return {x:m.getAttribute('x'),y:m.getAttribute('y'),w:m.getAttribute('width'),h:m.getAttribute('height')};})()"""))
print("edge bbox:", ev("""(function(){var g=document.querySelector('#stage svg .alur-layer-edges');
 if(!g) return null; var b=g.getBBox(); return {x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height)};})()"""))
print("edge d:", ev("""(function(){var out=[];Array.prototype.forEach.call(document.querySelectorAll('#stage svg .alur-layer-edges path'),function(p){out.push(p.getAttribute('d'))});return out;})()"""))
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
