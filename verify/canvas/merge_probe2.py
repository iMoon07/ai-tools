import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9606; PROF="/tmp/alur-probes/prof-merge2"
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
    return ev("""(()=>{try{return JSON.parse(document.getElementById('specBox').value);}catch(e){return null;}})()""")
def state(tag):
    sp = spec() or {}
    nodes = sp.get('nodes') or {}
    edges = sp.get('edges') or []
    shapes = {}
    for k in nodes: shapes[nodes[k].get('shape')] = shapes.get(nodes[k].get('shape'),0)+1
    print(tag, "module:", sp.get('module'), "nodes:", len(nodes), shapes, "edges:", len(edges),
          "heads:", ev("document.querySelectorAll('#stage .alur-edge-head').length"),
          "cards:", ev("document.querySelectorAll('.alur-module-embed').length"),
          "tableNodes:", ev("document.querySelectorAll('#stage .alur-table-node').length"))
ev("(()=>{const s=document.getElementById('preset'); s.value='canvas:blank'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(1.2)
state("blank:")
for mod in ('flow','reverse-proxy','chart','pipeline','graph','table'):
    ev(f"(()=>{{const b=document.querySelector('[data-scene-module={mod}]'); if(b) b.click();}})()")
    time.sleep(1.0); state(f"+block {mod}:")
for mod in ('canvas','flow','reverse-proxy','chart','pipeline','graph'):
    ev(f"(()=>{{const b=[...document.querySelectorAll('#templateLibrary [data-tpl-module={mod}]')]; if(b.length) b[b.length-1].click();}})()")
    time.sleep(1.0); state(f"+tpl {mod}:")
print("exceptions:", len(errs))
ws.close(); proc.terminate()
