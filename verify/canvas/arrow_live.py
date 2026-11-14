import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9627; PROF="/tmp/kilo/prof-arrowlive"
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
ev("(()=>{const s=document.getElementById('preset'); s.value='canvas:blank'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(1.2)
ev("document.querySelector('.tool[data-tool=arrow]').click()"); time.sleep(0.3)
stg = ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y};})()")
x1,y1 = stg['x']+200, stg['y']+300
x2,y2 = stg['x']+500, stg['y']+500
send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1)
for i in range(1,9):
    send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/8,y=y1+(y2-y1)*i/8,button="left")
    time.sleep(0.05)
print("during drag -> previews:", ev("document.querySelectorAll('.alur-preview-path').length"),
      "| d:", ev("(()=>{const p=document.querySelector('.alur-preview-path'); return p?p.getAttribute('d'):null;})()"))
send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1)
time.sleep(1.2)
print("after release -> edges:", ev("""(()=>{try{const s=JSON.parse(localStorage.getItem('ruang.scene.v1')||'{}');return JSON.stringify({n:(s.edges||[]).length,last:(s.edges||[]).slice(-1)[0]});}catch(e){return 'err';}})()"""),
      "heads:", ev("document.querySelectorAll('#stage .alur-edge-head').length"))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
