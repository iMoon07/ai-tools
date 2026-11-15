import json,time,urllib.request,subprocess,tempfile
import websocket
PORT=9785
tmp=tempfile.mkdtemp(prefix="lt")
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
def ev(e):
    r=cmd("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
cmd("Page.enable");cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",width=1400,height=900,deviceScaleFactor=1,mobile=False)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html?cb="+str(time.time()))
time.sleep(3.4)
ev("window.__errs=[];addEventListener('error',function(e){window.__errs.push(String(e.message));});")
def bg(sel):
    return ev("(function(){var e=document.querySelector(%s);return e?getComputedStyle(e).backgroundColor:null;})()" % json.dumps(sel))
print("dark shape:", bg('#shapePanel'), "assets:", bg('#panelAssets'))
ev("document.body.classList.add('theme--light')")
time.sleep(0.5)
print("light shape:", bg('#shapePanel'), "assets:", bg('#panelAssets'))
print("errs:", ev("window.__errs"))
proc.terminate()
