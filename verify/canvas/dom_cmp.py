import json, subprocess, time, urllib.parse, urllib.request, shutil, websocket
PORT=9630; PROF="/tmp/alur-probes/prof-domcmp"
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
                d=r["params"]["exceptionDetails"]; errs.append(d.get("text"))
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
ev("document.querySelector('[data-scene-module=table]').click()"); time.sleep(1.2)
ev("document.querySelector('[data-scene-module=chart]').click()"); time.sleep(2.0)
print("grid:", ev("""(()=>{const g=document.querySelector('.alur-canvas-grid'); if(!g) return 'none';
  const r=g.getBoundingClientRect(); return JSON.stringify({x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height),fill:g.getAttribute('fill')});})()"""))
print("table node:", ev("""(()=>{const g=document.querySelector('.alur-table-node'); if(!g) return 'none';
  const b=g.querySelector('.alur-table-box');
  return JSON.stringify({tr:g.getAttribute('transform'), boxFill:b.getAttribute('fill'), boxStroke:b.getAttribute('stroke')});})()"""))
print("chart node:", ev("""(()=>{const g=document.querySelector('.alur-chart-node'); if(!g) return 'none';
  const b=g.querySelector('.alur-chart-box'); const fo=g.querySelector('.alur-chart-fo');
  const emb=g.querySelector('.alur-module-embed'); const host=g.querySelector('.alur-host');
  const svg=g.querySelector('.alur-module-embed svg');
  const cs=e=>e?getComputedStyle(e):null;
  return JSON.stringify({tr:g.getAttribute('transform'), boxFill:b.getAttribute('fill'),
    fo:[fo.getAttribute('x'),fo.getAttribute('y'),fo.getAttribute('width'),fo.getAttribute('height')],
    embBg:emb?cs(emb).backgroundColor:null, hostBg:host?cs(host).backgroundColor:null,
    svgBg:svg?cs(svg).backgroundColor:null, svgViewBox:svg?svg.getAttribute('viewBox'):null,
    svgRects:svg?svg.querySelectorAll('rect').length:0,
    firstRectFill:svg&&svg.querySelector('rect')?svg.querySelector('rect').getAttribute('fill'):null,
    foStyle:fo?cs(fo).overflow:null});})()"""))
print("exceptions:", len(errs))
ws.close(); proc.terminate()
