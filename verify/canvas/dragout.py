import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9840; PROF="/tmp/alur-probes/prof-dragout"
shutil.rmtree(PROF, ignore_errors=True)
proc=subprocess.Popen(["chromium","--headless=new",f"--remote-debugging-port={PORT}",f"--user-data-dir={PROF}",
 "--no-first-run","--no-default-browser-check","--disable-gpu","--window-size=1600,1000",
 "--remote-allow-origins=*","--hide-scrollbars","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
import websocket
def http(p,m="GET"):
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{p}",method=m),timeout=10).read())
for _ in range(80):
    try: http("/json/version"); break
    except Exception: time.sleep(0.3)
t=http("/json/new?"+urllib.parse.quote("about:blank",safe=""),"PUT")
ws=websocket.create_connection(t["webSocketDebuggerUrl"],timeout=60,suppress_origin=True)
n=[0]; exc=[]
def send(m,**p):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]: return r.get("result",{})
        if r.get("method")=="Runtime.exceptionThrown":
            d=r["params"]["exceptionDetails"]; exc.append(d.get("text","")+" "+(d.get("exception") or {}).get("description","")[:180])
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.0)

ev("document.querySelector('[data-tool=line]').click()"); time.sleep(0.4)

VB = "(()=>{const s=document.querySelector('#stage svg'); const vb=s.viewBox.baseVal; return [Math.round(vb.x),Math.round(vb.y),Math.round(vb.width),Math.round(vb.height)];})()"

print("drag:", json.dumps(ev("""(async()=>{
  const stage=document.getElementById('stage'); const r=stage.getBoundingClientRect();
  const mk=(t,x,y)=>new PointerEvent(t,{bubbles:true,cancelable:true,pointerId:2,pointerType:'mouse',isPrimary:true,button:0,buttons:1,clientX:x,clientY:y});
  const x0=r.left+200, y0=r.top+200;
  stage.dispatchEvent(mk('pointerdown',x0,y0));
  for (let i=1;i<=10;i++) { window.dispatchEvent(mk('pointermove', x0+i*200, y0+i*70)); await new Promise(r=>setTimeout(r,16)); }
  window.dispatchEvent(mk('pointerup', x0+2000, y0+700));
  await new Promise(r=>setTimeout(r,500));
  const s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));
  const e=(s.edges||[]).slice(-1)[0]||{};
  return {stage:[Math.round(r.width),Math.round(r.height)], edges:(s.edges||[]).length,
          points:e.points, zoom:s.zoom, panX:Math.round(s.panX||0), panY:Math.round(s.panY||0),
          w:s.width, h:s.height};
})()""")))
print("viewBox before fit:", json.dumps(ev(VB)))
ev("document.getElementById('zoomFit').click()"); time.sleep(0.9)
print("viewBox after fit:", json.dumps(ev(VB)))
print("edge paths:", ev("document.querySelectorAll('#stage svg .alur-canvas-edge').length"))
print("exc:", exc if exc else "none")
proc.terminate()
