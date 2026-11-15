import json,time,urllib.request,subprocess,tempfile,base64
import websocket
PORT=9799
tmp=tempfile.mkdtemp(prefix="half2")
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
cmd("Page.enable");cmd("Runtime.enable")
for w,h,name in [(900,800,"900"),(700,800,"700")]:
    cmd("Emulation.setDeviceMetricsOverride",width=w,height=h,deviceScaleFactor=1,mobile=False)
    cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html?cb="+str(time.time()))
    time.sleep(3.2)
    s=cmd("Page.captureScreenshot",format="png")
    open("/tmp/alur-probes/half_%s.png"%name,"wb").write(base64.b64decode(s["data"]))
    print("saved", name)
proc.terminate()
