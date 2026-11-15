import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9669; PROF="/tmp/alur-probes/prof-gridclick"
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
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.5)
print("grid:", ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')).grid"))
print("btn rect:", ev("(()=>{const b=document.getElementById('gridToggle');const r=b.getBoundingClientRect();return [Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)];})()"))
print("hit at centre:", ev("""(function(){const b=document.getElementById('gridToggle');const r=b.getBoundingClientRect();
  const e=document.elementFromPoint(r.x+r.width/2, r.y+r.height/2);
  const chain=[];let c=e;while(c&&chain.length<5){chain.push(c.tagName.toLowerCase()+(c.id?'#'+c.id:''));c=c.parentElement;}
  const cs=getComputedStyle(b); return {chain:chain.join(' < '), pe:cs.pointerEvents, same:e===b};})()"""))
r = ev("(()=>{const b=document.getElementById('gridToggle');const r=b.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};})()")
send("Input.dispatchMouseEvent",type="mousePressed",x=r['x'],y=r['y'],button="left",clickCount=1,buttons=1)
send("Input.dispatchMouseEvent",type="mouseReleased",x=r['x'],y=r['y'],button="left",clickCount=1,buttons=0)
time.sleep(0.8)
for i in range(4):
    time.sleep(1.0)
    print("  t+%ds grid:" % (i+1), ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')).grid"),
          "| rect:", ev("(()=>{const g=document.querySelector('#stage .alur-canvas-grid');return g?[g.getAttribute('width'),g.getAttribute('height')]:null;})()"),
          "| ls:", ev("JSON.parse(localStorage.getItem('ruang.scene.v1')).grid"))
send("Input.dispatchMouseEvent",type="mousePressed",x=r['x'],y=r['y'],button="left",clickCount=1,buttons=1)
send("Input.dispatchMouseEvent",type="mouseReleased",x=r['x'],y=r['y'],button="left",clickCount=1,buttons=0)
time.sleep(1.2)
print("2nd click -> grid:", ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')).grid"))
send("Input.dispatchMouseEvent",type="mousePressed",x=r['x'],y=r['y'],button="right",clickCount=1,buttons=2)
send("Input.dispatchMouseEvent",type="mouseReleased",x=r['x'],y=r['y'],button="right",clickCount=1,buttons=0)
time.sleep(0.8)
print("right click -> grid:", ev("JSON.parse(document.getElementById('stage').getAttribute('data-spec')).grid"))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
