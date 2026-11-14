import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9662; PROF="/tmp/kilo/prof-dock"
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
for w,h in ((1500,1000),(1366,768),(1024,712)):
    send("Emulation.setDeviceMetricsOverride",width=w,height=h,deviceScaleFactor=1,mobile=False)
    send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4)
    print("== %dx%d ==" % (w,h))
    print(ev("""(function(){
      var out=[];
      ['panelAssets','panelLayers','panelScene','shapePanel','editorBar','topbar','minimap','viewBar','stage'].forEach(function(id){
        var e=document.getElementById(id); if(!e) return;
        var r=e.getBoundingClientRect(); var c=getComputedStyle(e);
        out.push([id, Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height), c.display, c.visibility, c.opacity, c.pointerEvents, c.transform.slice(0,28)]);
      });
      return JSON.stringify(out);})()"""))
ws.close(); proc.terminate()
