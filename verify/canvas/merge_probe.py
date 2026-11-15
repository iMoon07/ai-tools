import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9605; PROF="/tmp/alur-probes/prof-merge"
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
def state(tag):
    print(tag, ev("""JSON.stringify({
      module: document.getElementById('stage').getAttribute('data-module'),
      nodes: document.querySelectorAll('#stage g[data-node-id]').length,
      cards: document.querySelectorAll('.alur-module-embed').length,
      edges: document.querySelectorAll('#stage .alur-edge').length,
      head: document.querySelectorAll('#stage .alur-edge-head').length,
      table: document.querySelectorAll('#stage .alur-table-node').length,
      cardText: !!document.body.textContent.match(/double-click to expand/)
    })"""))
# start from blank canvas
ev("(()=>{const s=document.getElementById('preset'); s.value='canvas:blank'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(1.2)
state("blank:")
for mod,label in (('flow','Flow'),('reverse-proxy','Reverse Proxy'),('chart','Chart'),('pipeline','Pipeline'),('graph','Graph'),('table','Table')):
    ev(f"(()=>{{const b=[...document.querySelectorAll('#sceneBlocks [data-block]')].find(x=>x.getAttribute('data-block')==='{mod}'); if(b) b.click();}})()")
    time.sleep(1.0)
    state(f"+{label}:")
# templates
for mod in ('canvas','flow','reverse-proxy','chart','pipeline','graph'):
    ev(f"(()=>{{const b=[...document.querySelectorAll('#templateLibrary [data-tpl-module={mod}]')]; if(b.length) b[b.length-1].click();}})()")
    time.sleep(1.0)
    state(f"tpl {mod}:")
print("exceptions:", len(errs))
ws.close(); proc.terminate()
