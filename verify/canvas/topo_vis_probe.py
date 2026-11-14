import json, subprocess, time, urllib.parse, urllib.request, shutil, base64
PORT=9551; PROF="/tmp/kilo/prof-vis"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1500,1000","--remote-allow-origins=*","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
import websocket
def http(p,method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=method),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=60,suppress_origin=True)
n=[0]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]:
            if r.get("method")=="Runtime.exceptionThrown": print("[exception]",r["params"]["exceptionDetails"].get("text"))
            if r.get("error"): raise RuntimeError(r["error"])
            return r.get("result",{})
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/topology.html")
time.sleep(4)
shot=send("Page.captureScreenshot",format="png",captureBeyondViewport=False)
open("/tmp/kilo/topo_ui_desktop.png","wb").write(base64.b64decode(shot["data"]))
# also capture the edges pane
send("Runtime.evaluate",expression="document.querySelector('.dock-tab[data-pane=edges]').click()")
time.sleep(1)
shot=send("Page.captureScreenshot",format="png",captureBeyondViewport=False)
open("/tmp/kilo/topo_ui_edges.png","wb").write(base64.b64decode(shot["data"]))
print("shots saved")
ws.close(); proc.terminate()
