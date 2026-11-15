import json, subprocess, time, urllib.parse, urllib.request, shutil, base64
PORT=9554; PROF="/tmp/alur-probes/prof-live2"
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
        if r.get("id")==n[0]: return r.get("result",{})
def ev(expr):
    r=send("Runtime.evaluate",expression=expr,returnByValue=True,awaitPromise=True)
    return r.get("result",{}).get("value")
send("Runtime.enable"); send("Page.enable")
for W,H,name in [(1500,1000,'desk'),(390,844,'mob')]:
    send("Emulation.setDeviceMetricsOverride",width=W,height=H,deviceScaleFactor=1,mobile=W<600)
    send("Page.navigate",url="http://127.0.0.1:8123/topology.html")
    time.sleep(3)
    ev("document.querySelector('.dock-tab[data-pane=json]').click()")
    time.sleep(0.6)
    print(name, "specBox:", ev("(()=>{const r=document.getElementById('specBox').getBoundingClientRect();return [Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)]})()"))
    print(name, "hOverflow:", ev("document.documentElement.scrollWidth > window.innerWidth + 1"))
    print(name, "status:", ev("document.getElementById('codeStatus').textContent"))
    if name=='desk':
        sh=send("Page.captureScreenshot",format="png")
        open("/tmp/alur-probes/topo_topology_tab.png","wb").write(base64.b64decode(sh["data"]))
ws.close(); proc.terminate()
