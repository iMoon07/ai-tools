import json, time, urllib.request, subprocess, tempfile, sys
import websocket
PORT=9482
W=int(sys.argv[1]); H=int(sys.argv[2])
tmp=tempfile.mkdtemp(prefix="dk")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
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
    if r.get("subtype")=="error": return {"__err":r.get("description")}
    return r.get("value")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.2)
print("== %dx%d ==" % (W,H))
for name in ['scene','assets','layers']:
    ev("document.querySelector('[data-panel=\"%s\"]').click()" % name)
    time.sleep(0.5)
    r = ev("""(function(){var d=document.querySelector('.dock.is-open'); if(!d) return 'none';
      var b=d.getBoundingClientRect(); var cs=getComputedStyle(d);
      return {id:d.id,x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height),
        pos:cs.position,bottom:cs.bottom,left:cs.left};})()""")
    print(" ", name, "->", r)
    ev("document.querySelector('[data-panel=\"%s\"]').click()" % name)
    time.sleep(0.35)
c.close(); proc.terminate()
