import json, subprocess, time, urllib.parse, urllib.request, shutil, base64
PORT=9620; PROF="/tmp/alur-probes/prof-toponew"
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
n=[0]; exc=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]: return r.get("result",{})
        if r.get("method")=="Runtime.exceptionThrown":
            d=r["params"]["exceptionDetails"]; exc.append(d.get("text","")+" "+(d.get("exception") or {}).get("description","")[:160])
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(3.4)

def probe(tag):
    print(tag, json.dumps(ev("""(()=>{
     const q=s=>document.querySelector(s);
     const r=e=>{if(!e)return null;const b=e.getBoundingClientRect();return [Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)]};
     const st=q('#stage'), dk=q('#dock');
     return {stage:r(st), stageStyle:[st.style.right,st.style.bottom],
       dockOpen:dk.classList.contains('is-open'), dockSide:dk.dataset.side, dock:r(dk),
       dockPe:getComputedStyle(dk).pointerEvents,
       tabs:r(q('#dockTabs')),
       preview:r(q('#preview')), nodes:document.querySelectorAll('#preview .topo-node').length,
       stageOverflow: st.scrollWidth>st.clientWidth+1};
    })()""")))

probe("closed  :")
ev("document.querySelector('.dock-tab[data-pane=nodes]').click()"); time.sleep(0.7)
probe("nodes   :")
ev("document.querySelector('.dock-tab[data-pane=edges]').click()"); time.sleep(0.7)
probe("edges   :")
ev("document.querySelector('.dock-tab[data-pane=look]').click()"); time.sleep(0.7)
probe("look    :")
ev("document.getElementById('dockClose').click()"); time.sleep(0.7)
probe("closed2 :")
open('/tmp/alur-probes/topo_new_desktop.png','wb').write(base64.b64decode(send("Page.captureScreenshot",format="png")["data"]))
print("exceptions:", exc)
ws.close(); proc.terminate()