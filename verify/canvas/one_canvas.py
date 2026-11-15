import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9624; PROF="/tmp/alur-probes/prof-onecanvas"
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
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("   [EXC]", d.get("text"), (d.get("exception") or {}).get("description","")[:180])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
vb0 = ev("document.querySelector('#stage svg').getAttribute('viewBox')")
ev("(()=>{const s=document.getElementById('preset'); s.value='canvas:blank'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(1.2)
print("after blank -> nodes:", ev("document.querySelectorAll('#stage [data-node-id]').length"))
for mod in ('flow','reverse-proxy','chart','pipeline','graph','table'):
    ev(f"document.querySelector('[data-scene-module={mod}]').click()"); time.sleep(1.1)
print("after all blocks:", ev("""JSON.stringify((()=>{const s=JSON.parse(localStorage.getItem('ruang.scene.v1')||'{}');const n=s.nodes||{};
  const sh={};Object.keys(n).forEach(k=>{sh[n[k].shape]=(sh[n[k].shape]||0)+1;});
  return {module:s.module,grid:s.grid,nodes:Object.keys(n).length,shapes:sh,edges:(s.edges||[]).length};})())"""))
for mod in ('canvas','flow','reverse-proxy','chart','pipeline','graph'):
    ev(f"(()=>{{const b=[...document.querySelectorAll('#templateLibrary [data-tpl-module={mod}]')]; if(b.length) b[0].click();}})()"); time.sleep(1.1)
print("after templates:", ev("""JSON.stringify((()=>{const s=JSON.parse(localStorage.getItem('ruang.scene.v1')||'{}');const n=s.nodes||{};
  const sh={};Object.keys(n).forEach(k=>{sh[n[k].shape]=(sh[n[k].shape]||0)+1;});
  return {module:s.module,grid:s.grid,nodes:Object.keys(n).length,shapes:sh,edges:(s.edges||[]).length};})())"""))
print("viewBox same:", vb0 == ev("document.querySelector('#stage svg').getAttribute('viewBox')"))
print("module nodes (cards):", ev("document.querySelectorAll('#stage .alur-module-node').length"))
print("chart node chrome:", ev("""(()=>{const g=document.querySelector('#stage .alur-chart-node'); if(!g) return 'none';
  const r=g.querySelector('.alur-chart-box');
  return JSON.stringify({rectFill:r.getAttribute('fill'),rectStroke:r.getAttribute('stroke'),
    svg:!!g.querySelector('.alur-module-embed svg'), texts:g.querySelectorAll('text').length});})()"""))
print("heads:", ev("document.querySelectorAll('#stage .alur-edge-head').length"))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
