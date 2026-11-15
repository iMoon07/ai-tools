import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9664; PROF="/tmp/alur-probes/prof-drawall"
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
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=180,suppress_origin=True)
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
def set_tool(t):
    return ev("(function(){var b=[].slice.call(document.querySelectorAll('[data-tool]')).filter(function(x){return x.getAttribute('data-tool')==='%s';})[0]; if(!b) return 'missing'; b.click(); return 'ok';})()" % t)
def drag(x1,y1,x2,y2,steps=8):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1,buttons=1)
    for i in range(1,steps+1):
        send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/steps,y=y1+(y2-y1)*i/steps,button="left",buttons=1); time.sleep(0.02)
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1,buttons=0); time.sleep(0.7)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.5)
def counts():
    return ev("({n:document.querySelectorAll('#stage .alur-node').length,h:document.querySelectorAll('#stage .alur-edge-head').length,d:document.querySelectorAll('#stage .alur-drawing').length,e:(JSON.parse(localStorage.getItem('ruang.scene.v1')).edges||[]).length})")
stg = ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()")
zones = {'TL':(0.03,0.10),'TC':(0.5,0.08),'TR':(0.96,0.10),'ML':(0.03,0.5),'C':(0.5,0.5),'MR':(0.95,0.5),'BL':(0.03,0.90),'BC':(0.5,0.92),'BR':(0.95,0.90)}
report = {}
for tool in ('arrow','box','circle','diamond','line','draw'):
    ok, bad = [], []
    for name,(fx,fy) in zones.items():
        set_tool(tool); time.sleep(0.2)
        x, y = stg['x']+stg['w']*fx, stg['y']+stg['h']*fy
        b = counts(); drag(round(x)-26, round(y)-18, round(x)+26, round(y)+18); a = counts()
        (ok if (a['n']-b['n'], a['h']-b['h'], a['d']-b['d'], a['e']-b['e']) != (0,0,0,0) else bad).append(name)
    report[tool] = {'ok': ok, 'blocked': bad}
    print(tool, '-> ok:', len(ok), '/9', '| blocked:', bad)
print("exceptions:", len(errs))
ws.close(); proc.terminate()
