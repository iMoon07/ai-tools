import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9665; PROF="/tmp/alur-probes/prof-grid"
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
def state():
    return ev("""(function(){
      var g=document.querySelector('#stage .alur-canvas-grid');
      var cs=g?getComputedStyle(g):null;
      var b=document.getElementById('gridToggle');
      return {grid:JSON.parse(document.getElementById('stage').getAttribute('data-spec')).grid,
              rect:g?[g.getAttribute('width'),g.getAttribute('height')]:null,
              display:cs?cs.display:null, opacity:cs?cs.opacity:null,
              btn:!!b, on:b?b.classList.contains('is-on'):null};})()""")
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.5)
print("initial:", state())
ev("document.getElementById('gridToggle').click()"); time.sleep(0.7)
print("after click:", state())
send("Input.dispatchKeyEvent",type="keyDown",code="Quote",key="'",windowsVirtualKeyCode=222,nativeVirtualKeyCode=222,modifiers=2)
send("Input.dispatchKeyEvent",type="keyUp",code="Quote",key="'",windowsVirtualKeyCode=222,nativeVirtualKeyCode=222,modifiers=2)
time.sleep(0.7)
print("after Ctrl+' :", state())
ev("document.getElementById('gridToggle').click()"); time.sleep(0.6)
send("Page.reload"); time.sleep(4.5)
print("after reload (expect off):", state())
ev("document.getElementById('gridToggle').click()"); time.sleep(0.6)
print("back on:", state())
print("exceptions:", len(errs))
ws.close(); proc.terminate()
