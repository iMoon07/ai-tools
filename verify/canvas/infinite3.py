import json, subprocess, time, urllib.parse, urllib.request, shutil
PORT=9853; PROF="/tmp/alur-probes/prof-inf3"
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

VB = "(()=>{const v=document.querySelector('#stage svg').viewBox.baseVal; return [Math.round(v.x),Math.round(v.y),Math.round(v.width),Math.round(v.height)];})()"

for w,h,mob,tag in ((1600,1000,False,"desktop"),(390,844,True,"mobile")):
    send("Emulation.setDeviceMetricsOverride",width=w,height=h,deviceScaleFactor=1,mobile=mob)
    exc.clear()
    send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.8)
    print(tag, "frame:", json.dumps(ev("""(()=>{const g=document.querySelector('#stage svg .alur-layer-page');
      if(!g) return 'missing';
      return {label:g.querySelector('.alur-page-label').textContent,
        rect:[g.querySelector('.alur-page-rect').getAttribute('width'), g.querySelector('.alur-page-rect').getAttribute('height')],
        pe:getComputedStyle(g).pointerEvents,
        ovfX: document.documentElement.scrollWidth>innerWidth};})()""")))

# drag past the right edge on desktop
send("Emulation.setDeviceMetricsOverride",width=1600,height=1000,deviceScaleFactor=1,mobile=False)
send("Page.navigate",url="http://127.0.0.1:8123/draw.html"); time.sleep(3.8)
print("auto-pan:", json.dumps(ev("""(async()=>{
  const stage=document.getElementById('stage'); const r=stage.getBoundingClientRect();
  const mk=(t,x,y)=>new PointerEvent(t,{bubbles:true,cancelable:true,pointerId:4,pointerType:'mouse',isPrimary:true,button:0,buttons:1,clientX:x,clientY:y});
  document.querySelector('[data-tool=line]').click();
  stage.dispatchEvent(mk('pointerdown', r.left+300, r.top+300));
  for (let i=0;i<14;i++) { window.dispatchEvent(mk('pointermove', r.right-25, r.top+320)); await new Promise(x=>setTimeout(x,45)); }
  const vb=document.querySelector('#stage svg').viewBox.baseVal;
  const during=Math.round(vb.x);
  window.dispatchEvent(mk('pointerup', r.right-25, r.top+320));
  await new Promise(x=>setTimeout(x,400));
  const s=JSON.parse(document.getElementById('stage').getAttribute('data-spec'));
  const e=(s.edges||[]).slice(-1)[0]||{};
  return {panDuring:during, endX: e.points?Math.round(e.points[e.points.length-1][0]):null,
          edges:(s.edges||[]).length};})()""")))

# fit after drawing outside
ev("document.getElementById('zoomFit').click()"); time.sleep(0.9)
print("after fit:", json.dumps(ev(VB)))
print("exc:", exc if exc else "none")
proc.terminate()
