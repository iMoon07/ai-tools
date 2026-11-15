import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9659; PROF="/tmp/alur-probes/prof-ov3"
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
JS = """(function(){
  var g=function(id){var e=document.getElementById(id); if(!e) return null; var r=e.getBoundingClientRect(); var c=getComputedStyle(e);
    return [id, Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height), c.pointerEvents, c.zIndex];};
  var ids=['stage','editorBar','topbar','minimap','viewBar','stageStatus','gridStatus','dropHint','zoomVal','panelAssets','panelScene','shapePanel'];
  return JSON.stringify(ids.map(g).filter(Boolean));
})()"""
print("rects:", ev(JS))
HIT = """(function(x,y){
  var e=document.elementFromPoint(__X__,__Y__); if(!e) return 'none';
  var chain=[]; var c=e;
  while(c && chain.length<6){ var cls=(c.getAttribute&&c.getAttribute('class'))?String(c.getAttribute('class')).trim().split(/\\s+/).slice(0,2).join('.'):'';
    chain.push(c.tagName.toLowerCase()+(c.id?'#'+c.id:'')+(cls?'.'+cls:'')); c=c.parentElement; }
  var r=e.getBoundingClientRect();
  return chain.join(' < ')+' | box '+Math.round(r.x)+','+Math.round(r.y)+' '+Math.round(r.width)+'x'+Math.round(r.height);
})(__X__,__Y__)"""
for (x,y) in [(60,150),(60,528),(60,860),(90,528),(400,528),(60,300),(60,700),(30,500),(1470,500),(750,528)]:
    js = HIT.replace('__X__', str(x)).replace('__Y__', str(y))
    print((x,y), '->', ev(js))
ws.close(); proc.terminate()
