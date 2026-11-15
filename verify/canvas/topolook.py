import json, subprocess, time, urllib.parse, urllib.request, shutil, base64, sys
PORT=9610; PROF="/tmp/alur-probes/prof-topolook"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1600,1000","--remote-allow-origins=*","--hide-scrollbars","about:blank"],
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
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.5)
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
print("layout:",json.dumps(ev("""(()=>{
 const q=s=>document.querySelector(s), r=e=>{if(!e)return null;const b=e.getBoundingClientRect();return [Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)]};
 return {win:[innerWidth,innerHeight],
  dock:r(q('#dock')), dockOpen:q('#dock')?q('#dock').className:null,
  board:r(q('#board')), preview:r(q('#preview')),
  canvas:r(q('#preview .topo-canvas')), stage:r(q('#preview .topo-stage')),
  nodes:[...document.querySelectorAll('#preview .topo-node')].map(x=>r(x)),
  panes:[...document.querySelectorAll('.pane')].map(p=>[p.dataset.pane,p.className,r(p)]),
  tabs:[...document.querySelectorAll('.dock-tab')].map(p=>[p.dataset.pane,p.className])
 }})()""")))
shot=send("Page.captureScreenshot",format="png").get("data")
open('/tmp/alur-probes/topo_look_desktop.png','wb').write(base64.b64decode(shot))
print("shot saved")
ws.close(); proc.terminate()