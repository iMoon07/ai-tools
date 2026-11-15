import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9850; PROF="/tmp/alur-probes/prof-inf"
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
            d=r["params"]["exceptionDetails"]; exc.append(d.get("text","")+" "+(d.get("exception") or {}).get("description","")[:200])
def ev(e):
    r=send("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True).get("result",{})
    return r.get("value") if r.get("subtype")!="error" else {"__err":r.get("description")}
send("Runtime.enable"); send("Page.enable")
send("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(4.0)

print("frame:", json.dumps(ev("""(()=>{const g=document.querySelector('#stage svg .alur-layer-page');
 if(!g) return 'missing';
 const r=g.querySelector('.alur-page-rect'), t=g.querySelector('.alur-page-label');
 const s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));
 return {rect:[r.getAttribute('width'), r.getAttribute('height')], label:t.textContent,
   spec:[s.width, s.height], btn:document.getElementById('pageToggle').getAttribute('aria-pressed')};})()""")))

print("toggle off:", json.dumps(ev("""(async()=>{document.getElementById('pageToggle').click();
 await new Promise(r=>setTimeout(r,400));
 return {present:!!document.querySelector('#stage svg .alur-layer-page'),
   pressed:document.getElementById('pageToggle').getAttribute('aria-pressed')};})()""")))
ev("document.getElementById('pageToggle').click()"); time.sleep(0.4)
print("toggle on:", ev("!!document.querySelector('#stage svg .alur-layer-page')"))

# drag a line past the right edge, hold near the edge, expect auto-pan
print("auto-pan:", json.dumps(ev("""(async()=>{
  const stage=document.getElementById('stage'); const r=stage.getBoundingClientRect();
  const before=JSON.parse(document.getElementById('stage').getAttribute('data-spec')).panX||0;
  const mk=(t,x,y)=>new PointerEvent(t,{bubbles:true,cancelable:true,pointerId:3,pointerType:'mouse',isPrimary:true,button:0,buttons:1,clientX:x,clientY:y});
  document.querySelector('[data-tool=line]').click();
  stage.dispatchEvent(mk('pointerdown', r.left+300, r.top+300));
  for (let i=0;i<12;i++) { window.dispatchEvent(mk('pointermove', r.right-20, r.top+320)); await new Promise(r=>setTimeout(r,40)); }
  const mid=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));
  window.dispatchEvent(mk('pointerup', r.right-20, r.top+320));
  await new Promise(r=>setTimeout(r,300));
  const e=(JSON.parse(document.getElementById('stage').getAttribute('data-spec')).edges||[]).slice(-1)[0]||{};
  return {panBefore:Math.round(before), panAfter:Math.round(mid.panX||0),
          endX: e.points? Math.round(e.points[e.points.length-1][0]) : null,
          zoom: mid.zoom};})()""")))
print("exc:", exc if exc else "none")
proc.terminate()
