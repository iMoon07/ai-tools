import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9615; PROF="/tmp/kilo/prof-livechart"
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
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text")); print("   [EXC]", d.get("text"), (d.get("exception") or {}).get("description","")[:200])
            return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
def spec():
    return ev("""(()=>{try{return JSON.parse(localStorage.getItem('ruang.scene.v1')||'{}');}catch(e){return null;}})()""")
def brief(tag):
    s = spec() or {}
    n = s.get('nodes') or {}
    ch = [v for v in n.values() if v.get('shape')=='chart']
    print(tag, "module:", s.get('module'), "grid:", s.get('grid'), "nodes:", len(n),
          "edges:", len(s.get('edges') or []),
          "chart:", ch and {k:ch[0].get(k) for k in ('label','chartType','dataSource','agg','groupBy')} or None,
          "chartSpec:", ch and (ch[0].get('staticSpec') or {}).get('labels'), ch and (ch[0].get('staticSpec') or {}).get('data'),
          "heads:", ev("document.querySelectorAll('#stage .alur-edge-head').length"),
          "stageModule:", ev("document.getElementById('stage').getAttribute('data-module')"))
# grid off
ev("""(()=>{const b=document.getElementById('gridToggle'); if(b){b.click();} })()"""); time.sleep(0.6)
brief("start:")
ev("document.querySelector('[data-scene-module=chart]').click()"); time.sleep(1.5)
brief("after +chart block:")
# add 4 boxes via template starter
ev("(()=>{const b=[...document.querySelectorAll('#templateLibrary [data-tpl-module=canvas]')][1]; b.click();})()"); time.sleep(1.5)
brief("after +starter(3 boxes):")
# cable change
ev("""(()=>{const c=document.getElementById('cable'); c.value='dashed'; c.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(1.2)
brief("after cable=dashed:")
ev("""(()=>{const c=document.getElementById('motion'); c.value='back'; c.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(1.2)
brief("after motion=back:")
print("exceptions:", len(errs))
ws.close(); proc.terminate()
