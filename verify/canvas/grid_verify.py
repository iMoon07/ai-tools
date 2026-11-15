import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9631; PROF="/tmp/alur-probes/prof-gridverify"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=1500,1000","--remote-allow-origins=*","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def http(p,method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=method),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=90,suppress_origin=True)
n=[0]; errs=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]:
            if r.get("method")=="Runtime.exceptionThrown":
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("   [EXC]", d.get("text"), (d.get("exception") or {}).get("description","")[:160])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
ev("(()=>{const s=document.getElementById('preset'); s.value='canvas:blank'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(1.2)
for mod in ('table','chart','flow'):
    ev(f"document.querySelector('[data-scene-module={mod}]').click()"); time.sleep(1.3)
print("spec:", ev("""(()=>{const s=JSON.parse(localStorage.getItem('ruang.scene.v1')||'{}');const n=s.nodes||{};
  return JSON.stringify({grid:s.grid, nodes:Object.keys(n).map(k=>({id:k,x:n[k].x,y:n[k].y,w:n[k].w,h:n[k].h,shape:n[k].shape}))});})()"""))
print("chart grid rects inside embed:", ev("document.querySelectorAll('#stage .alur-chart-node .alur-canvas-grid').length"))
print("canvas grid:", ev("document.querySelectorAll('#stage > svg > .alur-canvas-grid, #stage svg .alur-canvas-grid').length"))
print("chart svg viewBox:", ev("(()=>{const s=document.querySelector('#stage .alur-chart-node .alur-module-embed svg'); return s?s.getAttribute('viewBox'):'none';})()"))
print("chart spec grid:", ev("(()=>{const d=document.querySelector('#stage .alur-chart-node .alur-module-embed'); if(!d) return 'none'; const s=JSON.parse(d.getAttribute('data-spec')); return JSON.stringify({grid:s.grid,type:s.type});})()"))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
