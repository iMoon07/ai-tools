import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9643; PROF="/tmp/alur-probes/prof-viewkeep"
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
def drag(x1,y1,x2,y2,steps=10):
    send("Input.dispatchMouseEvent",type="mousePressed",x=x1,y=y1,button="left",clickCount=1)
    for i in range(1,steps+1):
        send("Input.dispatchMouseEvent",type="mouseMoved",x=x1+(x2-x1)*i/steps,y=y1+(y2-y1)*i/steps,button="left")
    send("Input.dispatchMouseEvent",type="mouseReleased",x=x2,y=y2,button="left",clickCount=1)
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
print("empty hint present:", ev("!!document.getElementById('emptyHint')"),
      "| dashed boxes:", ev("document.querySelectorAll('.empty-hint').length"))
ev("(()=>{const s=document.getElementById('preset'); s.value='canvas:blank'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(1.2)
ev("document.querySelector('[data-scene-module=flow]').click()"); time.sleep(1.4)
# zoom/pan away from fit
ev("""(()=>{const s=JSON.parse(localStorage.getItem('ruang.scene.v1')||'{}');
  s.zoom=0.6; s.panX=300; s.panY=200; localStorage.setItem('ruang.scene.v1',JSON.stringify(s));})()""")
send("Page.reload"); time.sleep(4)
vb0 = ev("(()=>{const v=document.querySelector('#stage svg').viewBox.baseVal; return [v.x,v.y,v.width,v.height].map(Math.round);})()")
print("view before arrow:", vb0)
stg = ev("(()=>{const r=document.getElementById('stage').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};})()")
ev("document.querySelector('.tool[data-tool=arrow]').click()"); time.sleep(0.3)
drag(stg['x']+stg['w']*0.2, stg['y']+stg['h']*0.7, stg['x']+stg['w']*0.5, stg['y']+stg['h']*0.4)
time.sleep(1.3)
vb1 = ev("(()=>{const v=document.querySelector('#stage svg').viewBox.baseVal; return [v.x,v.y,v.width,v.height].map(Math.round);})()")
print("view after arrow:", vb1, "| same:", vb0==vb1, "| edges:", ev("document.querySelectorAll('#stage .alur-edge').length"))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
