import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9870
tmp=tempfile.mkdtemp(prefix="pf")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=1200,900","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
cmd("Emulation.setDeviceMetricsOverride",width=1200,height=900,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/__probe_fit.html"); time.sleep(3)
print("viewBox:", ev("document.querySelector('#host svg').getAttribute('viewBox')"))
print("layers:", ev("""(function(){var s=document.querySelector('#host svg');
 return Array.prototype.map.call(s.children,function(c){return c.getAttribute('class')||c.tagName;});
})()"""))
print("mask:", ev("""(function(){var m=document.querySelector('#host svg mask');
 if(!m) return null;
 return {x:m.getAttribute('x'),y:m.getAttribute('y'),width:m.getAttribute('width'),height:m.getAttribute('height'),
         units:m.getAttribute('maskUnits')};})()"""))
print("edge bbox:", ev("""(function(){var g=document.querySelector('#host svg .alur-layer-edges');
 if(!g) return null; var b=g.getBBox(); return {x:b.x,y:b.y,w:b.width,h:b.height};})()"""))
print("svg bbox:", ev("""(function(){var g=document.querySelector('#host svg');
 try{var b=g.getBBox(); return {x:b.x,y:b.y,w:b.width,h:b.height};}catch(e){return String(e);}})()"""))
print("root bbox:", ev("""(function(){var b=document.querySelector('#host svg').getBoundingClientRect();
 return {x:b.x,y:b.y,w:b.width,h:b.height};})()"""))
# is the far edge actually visible? sample the rendered pixels is hard; instead check
# whether the edge path lies inside the mask rect region
print("far edge d:", ev("""(function(){var ps=document.querySelectorAll('#host svg .alur-layer-edges path');
 var out=[]; Array.prototype.forEach.call(ps,function(p){out.push(p.getAttribute('d'));});
 return out;})()"""))
c.close(); proc.terminate()
