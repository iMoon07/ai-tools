import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9961
tmp=tempfile.mkdtemp(prefix="m2")
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
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("window.__errs=[]; addEventListener('error',e=>window.__errs.push(String(e.message))); 'ok'")

info = ev("""(function(){
 var paths=Array.prototype.slice.call(document.querySelectorAll('#stage .alur-canvas-edge'));
 return paths.map(function(p){var b=p.getBBox();var m=p.getScreenCTM();
   var pt=document.querySelector('#stage svg').createSVGPoint();
   pt.x=b.x+b.width/2; pt.y=b.y+b.height/2;
   var q=pt.matrixTransform(m);
   return {d:p.getAttribute('d'), cx:q.x, cy:q.y};});
})()""")
print("edge paths:", len(info) if info else info)
if info:
    t = info[0]
    print("target d:", t["d"])
    x,y = t["cx"], t["cy"]
    print("client:", x, y)
    print("elementFromPoint:", ev("(function(){var e=document.elementFromPoint(%f,%f);return e?e.getAttribute('class')+'|'+(e.getAttribute('data-edge')||''):'none';})()" % (x,y)))
    before = ev("document.querySelector('#stage .alur-canvas-edge').getAttribute('d')")
    cmd("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=1)
    for k in range(1,7):
        cmd("Input.dispatchMouseEvent", type="mouseMoved", x=x+80*k/6.0, y=y+50*k/6.0, button="left", buttons=1)
        time.sleep(0.03)
    cmd("Input.dispatchMouseEvent", type="mouseReleased", x=x+80, y=y+50, button="left", clickCount=1)
    time.sleep(0.5)
    after = ev("document.querySelector('#stage .alur-canvas-edge').getAttribute('d')")
    print("before:", before)
    print("after :", after)
    print("moved :", before != after)
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
