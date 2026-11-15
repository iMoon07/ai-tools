import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9640; PROF="/tmp/alur-probes/prof-norm2"
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
SCENE = """(()=>{try{localStorage.setItem('ruang.scene.v1', %s);}catch(e){}})();""" % json.dumps(json.dumps({
  "module":"flow","title":"My Proxy","grid":True,"zoom":1,"panX":0,"panY":0,
  "nodes":{"client":{"label":"Client","sub":"browser","logo":"stack:github","color":"blue"},
           "proxy":{"label":"Proxy","sub":"edge","logo":"stack:nginx","color":"cyan"},
           "be1":{"label":"BE 1","sub":"api","color":"green"}},
  "edges":[{"from":"client","to":"proxy"}]}))
send("Page.addScriptToEvaluateOnNewDocument",source=SCENE)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.5)
print(ev("""JSON.stringify((()=>{const s=JSON.parse(localStorage.getItem('ruang.scene.v1')||'{}');
  return {module:s.module, mod:document.getElementById('stage').getAttribute('data-module'),
    labels:Object.values(s.nodes||{}).map(n=>n.label), edges:(s.edges||[]).length};})())"""))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
