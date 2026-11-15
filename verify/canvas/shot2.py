import json, time, urllib.request, subprocess, tempfile, sys, base64
import websocket
PORT=9990
W=int(sys.argv[1]); H=int(sys.argv[2]); OUT=sys.argv[3]; MOBILE=W<700
tmp=tempfile.mkdtemp(prefix="s2")
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
    if r.get("subtype")=="error": print("JS ERROR:",r.get("description"))
    return r.get("value")
cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=MOBILE)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
ev("document.querySelector(String.fromCharCode(91)+String.fromCharCode(100)+String.fromCharCode(97)+String.fromCharCode(116)+String.fromCharCode(97)+String.fromCharCode(45)+String.fromCharCode(112)+String.fromCharCode(97)+String.fromCharCode(110)+String.fromCharCode(101)+String.fromCharCode(108)+String.fromCharCode(61)+String.fromCharCode(34)+String.fromCharCode(115)+String.fromCharCode(99)+String.fromCharCode(101)+String.fromCharCode(110)+String.fromCharCode(101)+String.fromCharCode(34)+String.fromCharCode(93)).click()")
time.sleep(0.8)
r=cmd("Page.captureScreenshot", format="png")
open(OUT,'wb').write(base64.b64decode(r["data"]))
print("saved", OUT)
c.close(); proc.terminate()
