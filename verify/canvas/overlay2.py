import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9658; PROF="/tmp/alur-probes/prof-ov2"
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
n=[0]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]: return r.get("result",{})
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)
    res=r.get("result",{})
    if res.get("subtype")=="error": print("[JSERR]", res.get("description","")[:300])
    return res.get("value")
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1500,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.5)
print("== stage + overlay rects ==")
print(ev("""(()=>{const g=id=>{const e=document.getElementById(id); if(!e) return null; const r=e.getBoundingClientRect(); const c=getComputedStyle(e); return [id,Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height),c.pointerEvents,c.zIndex];};
 const ids=['stage','editorBar','topbar','minimap','viewBar','stageStatus','gridStatus','dropHint','zoomVal','leftRail','toolRail','panelAssets','panelScene','shapePanel'];
 return JSON.stringify(ids.map(g).filter(Boolean));})()"""))
print("\n== elementFromPoint at the failing box/circle spots ==")
for (x,y) in [(60,150),(60,528),(60,860),(90,528),(400,528),(60,300),(60,700)]:
    print((x,y), ev("""(()=>{const e=document.elementFromPoint(%d,%d); if(!e) return 'none';
      const chain=[];let c=e;while(c&&chain.length<6){chain.push(c.tagName.toLowerCase()+(c.id?'#'+c.id:'')+(c.getAttribute&&c.getAttribute('class')?'.'+String(c.getAttribute('class')).trim().split(/\\s+/).slice(0,2).join('.'):''));c=c.parentElement;}
      const r=e.getBoundingClientRect(); return chain.join(' < ')+'  @['+[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height))+']';})()""" % (x,y)))
ws.close(); proc.terminate()
