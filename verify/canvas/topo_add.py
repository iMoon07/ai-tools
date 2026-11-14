import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9674; PROF="/tmp/kilo/prof-topoadd"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",
 f"--user-data-dir={PROF}","--no-first-run","--no-default-browser-check","--disable-gpu",
 "--window-size=390,844","--remote-allow-origins=*","about:blank"],
 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def http(p,method="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=method),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),method="PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=120,suppress_origin=True)
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
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:300])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
send("Page.addScriptToEvaluateOnNewDocument", source="window.confirm=function(){return true;};window.alert=function(){};")
send("Emulation.setDeviceMetricsOverride",width=390,height=844,deviceScaleFactor=2,mobile=True)
send("Page.navigate",url="http://127.0.0.1:8123/topology.html"); time.sleep(4.5)
print("nodes:", ev("document.querySelectorAll('#preview .topo-node').length"))
ev("document.getElementById('dockToggle').click()"); time.sleep(0.8)
print("addNode rect:", ev("(()=>{const b=document.getElementById('addNode');const r=b.getBoundingClientRect();return [Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)];})()"))
b = ev("document.querySelectorAll('#preview .topo-node').length")
print("direct click addNode:", ev("(()=>{document.getElementById('addNode').click(); return 1;})()")); time.sleep(0.9)
a = ev("document.querySelectorAll('#preview .topo-node').length")
print("nodes:", b, "->", a)
print("starter:", ev("(()=>{const s=document.getElementById('presetSel'); s.value='fan'; s.dispatchEvent(new Event('change',{bubbles:true})); return 1;})()")); time.sleep(1.2)
print("after starter fan:", ev("document.querySelectorAll('#preview .topo-node').length"))
print("edges:", ev("document.querySelectorAll('#preview .topo-edge, #preview .topo-cable').length"))
print("stage:", ev("(()=>{const s=document.getElementById('stage');return {sh:s.scrollHeight,ch:s.clientHeight};})()"))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
