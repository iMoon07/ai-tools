import json, time, urllib.request, subprocess, tempfile
import websocket
PORT=9470
tmp=tempfile.mkdtemp(prefix="rz")
proc=subprocess.Popen(["chromium","--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
 "--remote-debugging-port=%d"%PORT,"--remote-allow-origins=*","--user-data-dir="+tmp,
 "--window-size=390,844","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
cmd("Emulation.setDeviceMetricsOverride",width=390,height=844,deviceScaleFactor=1,mobile=True)
cmd("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.5)
print("mobile rail kids:", ev("document.getElementById('editorBar').children.length"),
      "grid kids:", ev("document.getElementById('toolGrid').children.length"))
cmd("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
time.sleep(1.0)
print("desktop rail kids:", ev("document.getElementById('editorBar').children.length"),
      "grid kids:", ev("document.getElementById('toolGrid').children.length"))
print("desktop rail disp:", ev("getComputedStyle(document.getElementById('editorBar')).display"))
print("desktop tabs disp:", ev("getComputedStyle(document.getElementById('mobileTabs')).display"))
print("desktop toggle disp:", ev("getComputedStyle(document.getElementById('panelToggle')).display"))
print("errors:", ev("window.__errs||[]"))
c.close(); proc.terminate()
