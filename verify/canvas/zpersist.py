import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9868
tmp=tempfile.mkdtemp(prefix="zp")
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
ev("""localStorage.setItem('ruang.canvas.v1', JSON.stringify(Object.assign(JSON.parse(localStorage.getItem('ruang.canvas.v1')||'{}'), {zoom: 2.57}))); 'ok'""")
cmd("Page.reload"); time.sleep(3.5)
print("loaded persisted zoom:", ev("JSON.parse(localStorage.getItem('ruang.canvas.v1')||'{}').zoom"))
# cause a save via a wheel pan
ev("""(function(){var s=document.getElementById('stage');var r=s.getBoundingClientRect();
 s.dispatchEvent(new WheelEvent('wheel',{bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2,deltaY:60,deltaMode:0}));return 1;})()""")
time.sleep(1.2)
print("after save zoom:", ev("JSON.parse(localStorage.getItem('ruang.canvas.v1')||'{}').zoom"))
c.close(); proc.terminate()
