import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9656; PROF="/tmp/alur-probes/prof-fa4"
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
def set_tool(name):
    return ev("""(()=>{const b=[...document.querySelectorAll('[data-tool]')].filter(x=>x.getAttribute('data-tool')==='%s')[0]; if(!b) return 'missing'; b.click(); return document.querySelector('[data-tool].is-on').getAttribute('data-tool');})()""" % name)
def drag(x1,y1,x2,y2,steps=10):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1,buttons=1)
    for i in range(1,steps+1):
        send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/steps,y=y1+(y2-y1)*i/steps,button="left",buttons=1)
        time.sleep(0.02)
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1,buttons=0)
    time.sleep(0.6)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.5)
stg = ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()")
def counts():
    return ev("({n:document.querySelectorAll('#stage .alur-node').length,e:document.querySelectorAll('#stage .alur-edge-head').length})")
pts = {'TL':(0.04,0.10),'TC':(0.5,0.10),'TR':(0.96,0.10),'ML':(0.04,0.5),'C':(0.5,0.5),'MR':(0.96,0.5),'BL':(0.04,0.90),'BC':(0.5,0.88),'BR':(0.95,0.88)}
for tool in ('arrow','box','circle','line','draw'):
    out={}
    for name,(fx,fy) in pts.items():
        set_tool(tool); time.sleep(0.25)
        x, y = stg['x']+stg['w']*fx, stg['y']+stg['h']*fy
        b = counts(); drag(round(x)-30, round(y)-22, round(x)+30, round(y)+22); a = counts()
        d = (a['n']-b['n'], a['e']-b['e'])
        out[name] = d if d != (0,0) else '--'
    print(tool, "->", out)
print("exceptions:", len(errs))
ws.close(); proc.terminate()
