import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9652; PROF="/tmp/kilo/prof-inf4"
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
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:200])
    return res.get("value")
def vb():
    return ev("(()=>{const v=document.querySelector('#stage svg').viewBox.baseVal; return [Math.round(v.x),Math.round(v.y),Math.round(v.width),Math.round(v.height)];})()")
def z(): return round(ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')).zoom"), 4)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
stg = ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()")
px, py = stg['x']+stg['w']*0.5, stg['y']+stg['h']*0.5
print("start zoom:", z())
for i in range(40):
    send("Input.dispatchMouseEvent",type="mouseWheel",x=px,y=py,deltaX=0,deltaY=200,modifiers=2); time.sleep(0.12)
time.sleep(0.6)
print("after 40 out -> zoom:", z(), "| vb:", vb(), "| floor expected 0.05 -> vb.w", round(stg['w']/0.05))
for i in range(60):
    send("Input.dispatchMouseEvent",type="mouseWheel",x=px,y=py,deltaX=0,deltaY=-120,modifiers=2); time.sleep(0.10)
time.sleep(0.6)
print("after 60 in  -> zoom:", z(), "| vb:", vb(), "| cap expected 4 -> vb.w", round(stg['w']/4))
ev("document.getElementById('zoomFit').click()"); time.sleep(0.6)
print("fit -> zoom:", z(), "| vb:", vb())
print("exceptions:", len(errs))
ws.close(); proc.terminate()
