import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9614; PROF="/tmp/alur-probes/prof-cross"
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
def spec():
    return ev("""(()=>{try{const s=JSON.parse(localStorage.getItem('ruang.scene.v1')||'{}');const n=s.nodes||{};
      const sh={};Object.keys(n).forEach(k=>{sh[n[k].shape]=(sh[n[k].shape]||0)+1;});
      return JSON.stringify({module:s.module,nodes:Object.keys(n).length,shapes:sh,edges:(s.edges||[]).length});}catch(e){return 'err';}})()""")
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
ev("(()=>{const s=document.getElementById('preset'); s.value='flow:stack4'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(1.5)
print("flow scene:", spec(), "module:", ev("document.getElementById('stage').getAttribute('data-module')"))
ev("document.querySelector('[data-scene-module=table]').click()"); time.sleep(1.5)
print("after +table:", spec(), "cards:", ev("document.querySelectorAll('#stage .alur-module-node').length"))
ev("(()=>{const b=[...document.querySelectorAll('#templateLibrary [data-tpl-module=pipeline]')].pop(); b.click();})()"); time.sleep(1.5)
print("after +pipeline tpl:", spec(), "cards:", ev("document.querySelectorAll('#stage .alur-module-node').length"))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
