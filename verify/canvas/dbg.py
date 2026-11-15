import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9992
W,H=390,844
tmp=tempfile.mkdtemp(prefix="dg")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=%d,%d"%(W,H),"about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=True)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("document.querySelector('[data-panel=\"scene\"]').click()")
time.sleep(1.0)
print(ev("""(function(){var d=document.getElementById('panelScene');var cs=getComputedStyle(d);var b=d.getBoundingClientRect();
 return {cls:d.className,tr:cs.transform,left:cs.left,right:cs.right,width:cs.width,
   rect:{l:Math.round(b.left),r:Math.round(b.right),t:Math.round(b.top),b:Math.round(b.bottom)},
   mq:matchMedia('(max-width: 700px)').matches};})()"""))
c.close(); proc.terminate()
