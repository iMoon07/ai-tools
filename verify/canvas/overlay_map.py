import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9657; PROF="/tmp/kilo/prof-ov"
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
print("== body children that sit above the stage ==")
print(ev("""(()=>{
  const out=[];
  [...document.body.children].forEach(el=>{
    const cs=getComputedStyle(el); if(cs.display==='none'||cs.visibility==='hidden') return;
    const r=el.getBoundingClientRect(); if(!r.width||!r.height) return;
    out.push({id:el.id||el.className.toString().split(' ')[0], tag:el.tagName.toLowerCase(),
      pos:cs.position, z:cs.zIndex, pe:cs.pointerEvents,
      box:[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)]});
  });
  return JSON.stringify(out,null,1);})()"""))
print("\n== fixed/absolute elements anywhere (top 40 by area) ==")
print(ev("""(()=>{
  const out=[];
  document.querySelectorAll('body *').forEach(el=>{
    const cs=getComputedStyle(el); if(cs.position!=='fixed'&&cs.position!=='absolute') return;
    if(cs.display==='none'||cs.visibility==='hidden'||parseFloat(cs.opacity)===0) return;
    const r=el.getBoundingClientRect(); if(r.width<4||r.height<4) return;
    out.push({id:el.id||String(el.className).split(' ')[0], pos:cs.position, z:cs.zIndex, pe:cs.pointerEvents,
      box:[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)]});
  });
  out.sort((a,b)=>b.box[2]*b.box[3]-a.box[2]*a.box[3]);
  return JSON.stringify(out.slice(0,25),null,1);})()"""))
ws.close(); proc.terminate()
