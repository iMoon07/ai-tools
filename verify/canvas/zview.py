import json, sys, time, urllib.request, subprocess, tempfile
import websocket
PORT=9867
tmp=tempfile.mkdtemp(prefix="zv")
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
print(ev("""(function(){
 var ids=['zoomOut','zoomVal','zoomIn','zoomFit'];
 var o={};
 ids.forEach(function(k){var b=document.getElementById(k).getBoundingClientRect();o[k]={w:Math.round(b.width),h:Math.round(b.height),top:Math.round(b.top)};});
 var bar=document.getElementById('viewBar').getBoundingClientRect();
 o.viewBar={h:Math.round(bar.height),w:Math.round(bar.width),bottom:Math.round(bar.bottom)};
 o.stageTop=Math.round(document.getElementById('stage').getBoundingClientRect().top);
 return o;})()"""))
c.close(); proc.terminate()
